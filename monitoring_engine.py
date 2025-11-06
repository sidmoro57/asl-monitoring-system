"""
Moteur de monitoring ASL - Health Check Engine.
Effectue les vérifications de santé des services avec détection rapide des pannes.
"""
import time
import requests
from typing import Dict, Optional, Tuple
from datetime import datetime


class HealthCheckResult:
    """Résultat d'un health check."""
    
    def __init__(self, success: bool, status_code: Optional[int] = None,
                 response_time: Optional[float] = None, error: Optional[str] = None):
        """
        Initialise un résultat de health check.
        
        Args:
            success: True si le check a réussi
            status_code: Code HTTP de la réponse
            response_time: Temps de réponse en secondes
            error: Message d'erreur si échec
        """
        self.success = success
        self.status_code = status_code
        self.response_time = response_time
        self.error = error
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convertit le résultat en dictionnaire."""
        return {
            "success": self.success,
            "status_code": self.status_code,
            "response_time": self.response_time,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


class ServiceMonitor:
    """Moniteur pour un service ASL spécifique."""
    
    def __init__(self, name: str, url: str, method: str = "GET",
                 expected_status: int = 200, timeout: int = 10,
                 critical: bool = True):
        """
        Initialise le moniteur de service.
        
        Args:
            name: Nom du service
            url: URL du endpoint de health check
            method: Méthode HTTP (GET, POST, etc.)
            expected_status: Code HTTP attendu pour succès
            timeout: Timeout en secondes
            critical: Si le service est critique
        """
        self.name = name
        self.url = url
        self.method = method.upper()
        self.expected_status = expected_status
        self.timeout = timeout
        self.critical = critical
        self.consecutive_failures = 0
        self.last_check_result: Optional[HealthCheckResult] = None
    
    def check_health(self) -> HealthCheckResult:
        """
        Effectue un health check du service.
        
        Returns:
            Résultat du health check
        """
        start_time = time.time()
        
        try:
            # Effectuer la requête HTTP
            response = requests.request(
                method=self.method,
                url=self.url,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            response_time = time.time() - start_time
            
            # Vérifier le code de statut
            if response.status_code == self.expected_status:
                result = HealthCheckResult(
                    success=True,
                    status_code=response.status_code,
                    response_time=response_time
                )
                self.consecutive_failures = 0
            else:
                result = HealthCheckResult(
                    success=False,
                    status_code=response.status_code,
                    response_time=response_time,
                    error=f"Status code {response.status_code} != {self.expected_status}"
                )
                self.consecutive_failures += 1
        
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            result = HealthCheckResult(
                success=False,
                response_time=response_time,
                error=f"Timeout après {self.timeout}s"
            )
            self.consecutive_failures += 1
        
        except requests.exceptions.ConnectionError as e:
            response_time = time.time() - start_time
            result = HealthCheckResult(
                success=False,
                response_time=response_time,
                error=f"Erreur de connexion: {str(e)}"
            )
            self.consecutive_failures += 1
        
        except Exception as e:
            response_time = time.time() - start_time
            result = HealthCheckResult(
                success=False,
                response_time=response_time,
                error=f"Erreur: {str(e)}"
            )
            self.consecutive_failures += 1
        
        self.last_check_result = result
        return result
    
    def get_status(self) -> Dict:
        """
        Retourne le statut actuel du service.
        
        Returns:
            Dictionnaire avec le statut du service
        """
        return {
            "name": self.name,
            "url": self.url,
            "critical": self.critical,
            "consecutive_failures": self.consecutive_failures,
            "last_check": self.last_check_result.to_dict() if self.last_check_result else None
        }


class MonitoringEngine:
    """Moteur principal de monitoring des services ASL."""
    
    def __init__(self, services_config: list, failure_threshold: int = 2):
        """
        Initialise le moteur de monitoring.
        
        Args:
            services_config: Liste des configurations de services
            failure_threshold: Nombre d'échecs avant déclenchement d'alerte
        """
        self.failure_threshold = failure_threshold
        self.monitors = []
        
        # Créer un moniteur pour chaque service
        for service in services_config:
            monitor = ServiceMonitor(
                name=service.get('name'),
                url=service.get('url'),
                method=service.get('method', 'GET'),
                expected_status=service.get('expected_status', 200),
                timeout=service.get('timeout', 10),
                critical=service.get('critical', True)
            )
            self.monitors.append(monitor)
    
    def check_all_services(self) -> Dict[str, HealthCheckResult]:
        """
        Vérifie tous les services.
        
        Returns:
            Dictionnaire {nom_service: résultat}
        """
        results = {}
        
        for monitor in self.monitors:
            result = monitor.check_health()
            results[monitor.name] = result
        
        return results
    
    def get_failing_services(self) -> list:
        """
        Retourne la liste des services en échec qui dépassent le seuil.
        
        Returns:
            Liste des moniteurs en échec
        """
        return [
            monitor for monitor in self.monitors
            if monitor.consecutive_failures >= self.failure_threshold
        ]
    
    def get_all_status(self) -> list:
        """
        Retourne le statut de tous les services.
        
        Returns:
            Liste des statuts de tous les services
        """
        return [monitor.get_status() for monitor in self.monitors]
    
    def get_service_monitor(self, service_name: str) -> Optional[ServiceMonitor]:
        """
        Récupère le moniteur d'un service par son nom.
        
        Args:
            service_name: Nom du service
            
        Returns:
            ServiceMonitor ou None si non trouvé
        """
        for monitor in self.monitors:
            if monitor.name == service_name:
                return monitor
        return None
