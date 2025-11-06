"""
Module de notification Slack pour les alertes ASL.
Envoie des notifications formatées avec contexte complet.
"""
import os
from datetime import datetime
from typing import Dict, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackNotifier:
    """Gestionnaire de notifications Slack pour alertes ASL."""
    
    def __init__(self, token: Optional[str] = None, channel: str = "#asl-alerts", 
                 enabled: bool = True, mention_channel: bool = True):
        """
        Initialise le notificateur Slack.
        
        Args:
            token: Token du bot Slack (ou depuis variable d'environnement)
            channel: Canal pour les notifications
            enabled: Active/désactive les notifications
            mention_channel: Mention @channel pour alertes critiques
        """
        self.channel = channel
        self.enabled = enabled
        self.mention_channel = mention_channel
        
        # Récupérer le token depuis l'environnement si non fourni
        self.token = token or os.getenv('SLACK_BOT_TOKEN')
        
        if self.enabled and self.token:
            self.client = WebClient(token=self.token)
        else:
            self.client = None
    
    def send_alert(self, service_name: str, incident_id: str, details: Dict, is_critical: bool = True):
        """
        Envoie une alerte de panne de service.
        
        Args:
            service_name: Nom du service en panne
            incident_id: ID de l'incident
            details: Détails de l'incident (URL, erreur, code HTTP, etc.)
            is_critical: Si le service est critique (pour @channel)
        """
        if not self.enabled or not self.client:
            return
        
        # Emoji et couleur selon criticité
        emoji = "🚨" if is_critical else "⚠️"
        color = "#FF0000" if is_critical else "#FFA500"
        
        # Message d'alerte
        mention = "<!channel> " if is_critical and self.mention_channel else ""
        text = f"{emoji} {mention}*ALERTE ASL: Service en panne*"
        
        # Construction du bloc formaté
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} ALERTE: {service_name} est DOWN",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Service:*\n{service_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Incident ID:*\n`{incident_id}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Heure:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Criticité:*\n{'🔴 CRITIQUE' if is_critical else '🟡 Avertissement'}"
                    }
                ]
            }
        ]
        
        # Ajouter les détails de l'erreur
        if details:
            details_text = ""
            if 'url' in details:
                details_text += f"*URL:* {details['url']}\n"
            if 'error' in details:
                details_text += f"*Erreur:* `{details['error']}`\n"
            if 'status_code' in details:
                details_text += f"*Code HTTP:* {details['status_code']}\n"
            if 'response_time' in details:
                details_text += f"*Temps de réponse:* {details['response_time']:.2f}s\n"
            
            if details_text:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": details_text
                    }
                })
        
        # Ajouter un divider et des actions recommandées
        blocks.extend([
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "⚡ *Actions recommandées:*\n• Vérifier les logs du service\n• Contrôler la disponibilité des dépendances\n• Escalader si nécessaire"
                }
            }
        ])
        
        try:
            self.client.chat_postMessage(
                channel=self.channel,
                text=text,
                blocks=blocks
            )
        except SlackApiError as e:
            print(f"Erreur lors de l'envoi de la notification Slack: {e.response['error']}")
    
    def send_recovery(self, service_name: str, incident_id: str, duration_seconds: float):
        """
        Envoie une notification de restauration de service.
        
        Args:
            service_name: Nom du service restauré
            incident_id: ID de l'incident résolu
            duration_seconds: Durée de l'incident en secondes
        """
        if not self.enabled or not self.client:
            return
        
        # Convertir la durée en format lisible
        duration_str = self._format_duration(duration_seconds)
        
        text = f"✅ *Service restauré: {service_name}*"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"✅ RÉSOLU: {service_name} est UP",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Service:*\n{service_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Incident ID:*\n`{incident_id}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Heure:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Durée:*\n{duration_str}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🎉 Le service est de nouveau opérationnel après {duration_str}"
                }
            }
        ]
        
        try:
            self.client.chat_postMessage(
                channel=self.channel,
                text=text,
                blocks=blocks
            )
        except SlackApiError as e:
            print(f"Erreur lors de l'envoi de la notification Slack: {e.response['error']}")
    
    def _format_duration(self, seconds: float) -> str:
        """
        Formate une durée en secondes en chaîne lisible.
        
        Args:
            seconds: Durée en secondes
            
        Returns:
            Chaîne formatée (ex: "2m 30s", "1h 15m")
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def test_connection(self) -> bool:
        """
        Teste la connexion Slack.
        
        Returns:
            True si la connexion fonctionne
        """
        if not self.enabled or not self.client:
            print("Notifications Slack désactivées")
            return False
        
        try:
            response = self.client.auth_test()
            print(f"✓ Connexion Slack OK - Bot: {response['user']}")
            return True
        except SlackApiError as e:
            print(f"✗ Erreur de connexion Slack: {e.response['error']}")
            return False
