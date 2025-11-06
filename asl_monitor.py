"""
Service de monitoring ASL - Point d'entrée principal.
Orchestre le monitoring en temps réel avec notifications Slack.
"""
import os
import sys
import time
import yaml
import logging
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

from monitoring_engine import MonitoringEngine, HealthCheckResult
from slack_notifier import SlackNotifier
from incident_tracker import IncidentTracker


class ASLMonitoringService:
    """Service principal de monitoring ASL temps réel."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialise le service de monitoring.
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        # Charger les variables d'environnement
        load_dotenv()
        
        # Charger la configuration
        self.config = self._load_config(config_path)
        
        # Configurer le logging
        self._setup_logging()
        
        # Initialiser les composants
        self.engine = MonitoringEngine(
            services_config=self.config['services'],
            failure_threshold=self.config['monitoring']['failure_threshold']
        )
        
        self.notifier = SlackNotifier(
            channel=self.config['slack']['channel'],
            enabled=self.config['slack']['enabled'],
            mention_channel=self.config['slack']['mention_channel']
        )
        
        self.tracker = IncidentTracker(
            incidents_dir=self.config['logging']['incidents_dir']
        )
        
        self.check_interval = self.config['monitoring']['check_interval']
        self.running = False
        
        logging.info("Service de monitoring ASL initialisé")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Charge la configuration depuis le fichier YAML.
        
        Args:
            config_path: Chemin vers le fichier de configuration
            
        Returns:
            Configuration en dictionnaire
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"Erreur: Fichier de configuration '{config_path}' introuvable")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Erreur lors du parsing du fichier de configuration: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """Configure le système de logging."""
        log_level = getattr(logging, self.config['logging']['level'])
        log_file = self.config['logging']['file']
        
        # Créer le répertoire des logs si nécessaire
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configuration du logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def start(self):
        """Démarre le service de monitoring."""
        self.running = True
        
        logging.info("=" * 80)
        logging.info("🚀 DÉMARRAGE DU SERVICE DE MONITORING ASL")
        logging.info("=" * 80)
        logging.info(f"Services surveillés: {len(self.config['services'])}")
        logging.info(f"Intervalle de vérification: {self.check_interval}s")
        logging.info(f"Seuil d'échecs: {self.engine.failure_threshold}")
        logging.info(f"Notifications Slack: {'✓ Activées' if self.config['slack']['enabled'] else '✗ Désactivées'}")
        
        # Tester la connexion Slack si activée
        if self.config['slack']['enabled']:
            self.notifier.test_connection()
        
        logging.info("=" * 80)
        logging.info("")
        
        try:
            self._monitoring_loop()
        except KeyboardInterrupt:
            logging.info("\n⚠️  Arrêt du service demandé par l'utilisateur")
            self.stop()
    
    def stop(self):
        """Arrête le service de monitoring."""
        self.running = False
        logging.info("Service de monitoring arrêté")
        
        # Afficher les statistiques finales
        stats = self.tracker.get_statistics()
        logging.info("\n📊 STATISTIQUES FINALES:")
        logging.info(f"  - Incidents totaux: {stats['total_incidents']}")
        logging.info(f"  - Incidents actifs: {stats['active_incidents']}")
        logging.info(f"  - Incidents résolus: {stats['resolved_incidents']}")
        if stats['resolved_incidents'] > 0:
            logging.info(f"  - Durée moyenne: {stats['average_duration_seconds']:.2f}s")
    
    def _monitoring_loop(self):
        """Boucle principale de monitoring."""
        while self.running:
            cycle_start = time.time()
            
            # Vérifier tous les services
            results = self.engine.check_all_services()
            
            # Analyser les résultats
            self._process_results(results)
            
            # Log du statut
            self._log_status()
            
            # Calculer le temps d'attente jusqu'au prochain cycle
            elapsed = time.time() - cycle_start
            sleep_time = max(0, self.check_interval - elapsed)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def _process_results(self, results: Dict[str, HealthCheckResult]):
        """
        Traite les résultats des health checks.
        
        Args:
            results: Dictionnaire {nom_service: résultat}
        """
        # Vérifier les services en échec
        failing_services = self.engine.get_failing_services()
        
        for monitor in failing_services:
            service_name = monitor.name
            
            # Si pas d'incident actif, en créer un et notifier
            if not self.tracker.has_active_incident(service_name):
                result = results[service_name]
                
                details = {
                    "url": monitor.url,
                    "error": result.error,
                    "status_code": result.status_code,
                    "response_time": result.response_time,
                    "consecutive_failures": monitor.consecutive_failures
                }
                
                # Créer l'incident
                incident_id = self.tracker.start_incident(service_name, details)
                
                # Logger
                logging.error(f"🚨 ALERTE: {service_name} DOWN - Incident {incident_id}")
                logging.error(f"   URL: {monitor.url}")
                logging.error(f"   Erreur: {result.error}")
                
                # Envoyer notification Slack
                self.notifier.send_alert(
                    service_name=service_name,
                    incident_id=incident_id,
                    details=details,
                    is_critical=monitor.critical
                )
        
        # Vérifier les services restaurés
        for monitor in self.engine.monitors:
            service_name = monitor.name
            
            # Si le service est OK mais a un incident actif
            if monitor.consecutive_failures == 0 and self.tracker.has_active_incident(service_name):
                incident = self.tracker.get_active_incident(service_name)
                
                # Terminer l'incident
                self.tracker.end_incident(service_name)
                
                # Calculer la durée
                start_time = datetime.fromisoformat(incident['start_time'])
                duration = (datetime.now() - start_time).total_seconds()
                
                # Logger
                logging.info(f"✅ RÉSOLU: {service_name} UP - Incident {incident['id']} résolu")
                logging.info(f"   Durée: {duration:.2f}s")
                
                # Envoyer notification Slack
                self.notifier.send_recovery(
                    service_name=service_name,
                    incident_id=incident['id'],
                    duration_seconds=duration
                )
    
    def _log_status(self):
        """Log le statut actuel de tous les services."""
        status_list = self.engine.get_all_status()
        
        # Compter les services UP et DOWN
        up_count = sum(1 for s in status_list if s['consecutive_failures'] == 0)
        down_count = len(status_list) - up_count
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"[{timestamp}] Status: {up_count} UP / {down_count} DOWN")
        
        # Logger les détails des services DOWN
        for status in status_list:
            if status['consecutive_failures'] > 0:
                logging.warning(f"  ⚠️  {status['name']}: {status['consecutive_failures']} échecs consécutifs")


def main():
    """Point d'entrée principal du programme."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🔍 SYSTÈME DE MONITORING ASL TEMPS RÉEL                  ║
║                                                               ║
║     Détection instantanée des arrêts critiques                ║
║     Notifications Slack automatiques                          ║
║     Traçabilité complète des incidents                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Démarrer le service
    service = ASLMonitoringService()
    service.start()


if __name__ == "__main__":
    main()
