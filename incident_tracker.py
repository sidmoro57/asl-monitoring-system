"""
Module de gestion des incidents ASL.
Gère l'historique, la traçabilité et la persistance des incidents.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class IncidentTracker:
    """Gestionnaire d'incidents pour traçabilité complète."""
    
    def __init__(self, incidents_dir: str = "incidents"):
        """
        Initialise le tracker d'incidents.
        
        Args:
            incidents_dir: Répertoire pour stocker l'historique des incidents
        """
        self.incidents_dir = incidents_dir
        self.active_incidents: Dict[str, Dict] = {}
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Crée le répertoire des incidents s'il n'existe pas."""
        os.makedirs(self.incidents_dir, exist_ok=True)
    
    def start_incident(self, service_name: str, details: Dict) -> str:
        """
        Démarre un nouvel incident.
        
        Args:
            service_name: Nom du service en panne
            details: Détails de l'incident (URL, erreur, etc.)
            
        Returns:
            ID unique de l'incident
        """
        incident_id = f"{service_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        incident = {
            "id": incident_id,
            "service": service_name,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": None,
            "details": details,
            "status": "active"
        }
        
        self.active_incidents[service_name] = incident
        self._save_incident(incident)
        
        return incident_id
    
    def end_incident(self, service_name: str, resolution_details: Optional[Dict] = None):
        """
        Termine un incident actif.
        
        Args:
            service_name: Nom du service restauré
            resolution_details: Détails optionnels sur la résolution
        """
        if service_name not in self.active_incidents:
            return
        
        incident = self.active_incidents[service_name]
        end_time = datetime.now()
        start_time = datetime.fromisoformat(incident["start_time"])
        
        incident["end_time"] = end_time.isoformat()
        incident["duration_seconds"] = (end_time - start_time).total_seconds()
        incident["status"] = "resolved"
        
        if resolution_details:
            incident["resolution"] = resolution_details
        
        self._save_incident(incident)
        del self.active_incidents[service_name]
    
    def has_active_incident(self, service_name: str) -> bool:
        """
        Vérifie si un service a un incident actif.
        
        Args:
            service_name: Nom du service
            
        Returns:
            True si un incident est actif pour ce service
        """
        return service_name in self.active_incidents
    
    def get_active_incident(self, service_name: str) -> Optional[Dict]:
        """
        Récupère l'incident actif pour un service.
        
        Args:
            service_name: Nom du service
            
        Returns:
            Détails de l'incident ou None
        """
        return self.active_incidents.get(service_name)
    
    def _save_incident(self, incident: Dict):
        """
        Sauvegarde un incident dans un fichier JSON.
        
        Args:
            incident: Données de l'incident à sauvegarder
        """
        filename = f"{incident['id']}.json"
        filepath = os.path.join(self.incidents_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(incident, f, indent=2, ensure_ascii=False)
    
    def get_incident_history(self, limit: int = 50) -> List[Dict]:
        """
        Récupère l'historique des incidents.
        
        Args:
            limit: Nombre maximum d'incidents à retourner
            
        Returns:
            Liste des incidents triés par date décroissante
        """
        incidents = []
        
        if not os.path.exists(self.incidents_dir):
            return incidents
        
        for filename in os.listdir(self.incidents_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.incidents_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        incident = json.load(f)
                        incidents.append(incident)
                except Exception:
                    continue
        
        # Trier par date de début décroissante
        incidents.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        
        return incidents[:limit]
    
    def get_statistics(self) -> Dict:
        """
        Calcule des statistiques sur les incidents.
        
        Returns:
            Dictionnaire avec statistiques (nombre total, durée moyenne, etc.)
        """
        history = self.get_incident_history(limit=1000)
        
        total_incidents = len(history)
        resolved_incidents = [i for i in history if i.get('status') == 'resolved']
        
        if resolved_incidents:
            durations = [i.get('duration_seconds', 0) for i in resolved_incidents]
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            min_duration = min(durations)
        else:
            avg_duration = max_duration = min_duration = 0
        
        return {
            "total_incidents": total_incidents,
            "resolved_incidents": len(resolved_incidents),
            "active_incidents": len(self.active_incidents),
            "average_duration_seconds": round(avg_duration, 2),
            "max_duration_seconds": round(max_duration, 2),
            "min_duration_seconds": round(min_duration, 2)
        }
