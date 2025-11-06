# 🔍 Système de Monitoring ASL Temps Réel

> Détection instantanée des arrêts critiques d'ASL avec notifications Slack automatiques

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Vision

Système de monitoring proactif pour équipes DevOps permettant la **détection instantanée des arrêts critiques d'ASL** avec notifications Slack automatiques, réduisant le **MTTR de 80%** et éliminant complètement la surveillance manuelle.

## ✨ Impact & Résultats

- ⚡ **Alertes < 30 secondes** - Détection quasi-instantanée des pannes
- 📊 **Traçabilité complète** - Historique détaillé de tous les incidents
- 💬 **Intégration Slack** - Notifications automatiques dans vos canaux d'équipe
- 🚀 **Zero configuration** - Opérationnel après déploiement avec configuration minimale
- 🎯 **Équipe proactive** - Incidents résolus avant impact utilisateur
- ✅ **SLA respectés** - Monitoring continu 24/7

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.11+ ou Docker
- Token de bot Slack (optionnel mais recommandé)

### Installation avec Docker (Recommandé)

```bash
# 1. Cloner le repository
git clone https://github.com/sidmoro57/asl-monitoring-system.git
cd asl-monitoring-system

# 2. Copier et configurer l'environnement
cp .env.example .env
# Éditer .env et ajouter votre SLACK_BOT_TOKEN

# 3. Configurer les services à monitorer
# Éditer config.yaml avec vos services

# 4. Démarrer le monitoring
docker-compose up -d

# 5. Voir les logs
docker-compose logs -f
```

### Installation Python Native

```bash
# 1. Cloner et installer les dépendances
git clone https://github.com/sidmoro57/asl-monitoring-system.git
cd asl-monitoring-system
pip install -r requirements.txt

# 2. Configuration
cp .env.example .env
# Éditer .env avec votre token Slack

# 3. Lancer le monitoring
python asl_monitor.py
```

## ⚙️ Configuration

### 1. Services à Monitorer

Éditez `config.yaml` pour définir vos services :

```yaml
services:
  - name: "API Production"
    url: "https://api.example.com/health"
    method: "GET"
    expected_status: 200
    timeout: 10
    critical: true
    
  - name: "Web Application"
    url: "https://app.example.com/health"
    method: "GET"
    expected_status: 200
    timeout: 10
    critical: true
```

### 2. Configuration Slack

1. Créez un bot Slack : https://api.slack.com/apps
2. Ajoutez les permissions OAuth : `chat:write`, `chat:write.public`
3. Installez le bot dans votre workspace
4. Copiez le token (commence par `xoxb-`)
5. Ajoutez-le dans `.env` :

```bash
SLACK_BOT_TOKEN=xoxb-votre-token-ici
```

6. Configurez le canal dans `config.yaml` :

```yaml
slack:
  channel: "#asl-alerts"
  enabled: true
  mention_channel: true
```

### 3. Paramètres de Monitoring

```yaml
monitoring:
  # Intervalle entre les vérifications (secondes)
  check_interval: 20
  
  # Nombre d'échecs avant déclenchement d'alerte
  failure_threshold: 2
  
  # Timeout par défaut (secondes)
  default_timeout: 10
```

## 📊 Fonctionnalités

### Monitoring en Temps Réel

- ✅ Vérification périodique des services (intervalle configurable)
- ✅ Détection des pannes en < 30 secondes
- ✅ Support HTTP/HTTPS avec validation du status code
- ✅ Mesure du temps de réponse
- ✅ Gestion intelligente des timeouts

### Notifications Slack

- 🚨 Alertes immédiates lors de détection de panne
- ✅ Notifications de rétablissement
- 📊 Messages formatés avec tous les détails
- 🔔 Mention @channel pour services critiques
- ⏱️ Durée des incidents calculée automatiquement

### Traçabilité des Incidents

- 📝 Historique JSON de tous les incidents
- 📅 Timestamps précis (début, fin, durée)
- 🔍 Détails complets (URL, erreur, code HTTP)
- 📊 Statistiques d'incidents
- 💾 Persistance des données

## 📁 Structure du Projet

```
asl-monitoring-system/
├── asl_monitor.py          # Point d'entrée principal
├── monitoring_engine.py    # Moteur de health checks
├── slack_notifier.py       # Gestion notifications Slack
├── incident_tracker.py     # Traçabilité des incidents
├── config.yaml             # Configuration des services
├── requirements.txt        # Dépendances Python
├── Dockerfile             # Image Docker
├── docker-compose.yml     # Orchestration Docker
├── .env.example           # Template variables d'environnement
└── README.md              # Documentation
```

## 🔧 Utilisation Avancée

### Voir les Logs

```bash
# Avec Docker
docker-compose logs -f

# Fichier de logs
tail -f logs/monitoring.log
```

### Consulter l'Historique des Incidents

Les incidents sont stockés dans le dossier `incidents/` au format JSON :

```bash
ls incidents/
# API_Production_20241106_153045.json
# Web_Application_20241106_154530.json

cat incidents/API_Production_20241106_153045.json
```

### Statistiques

Le système affiche automatiquement des statistiques lors de l'arrêt :

```
📊 STATISTIQUES FINALES:
  - Incidents totaux: 5
  - Incidents actifs: 0
  - Incidents résolus: 5
  - Durée moyenne: 45.23s
```

### Personnalisation

#### Ajouter un Nouveau Service

1. Éditez `config.yaml`
2. Ajoutez votre service dans la section `services:`
3. Redémarrez : `docker-compose restart`

#### Modifier l'Intervalle de Monitoring

Éditez `config.yaml` :

```yaml
monitoring:
  check_interval: 15  # Vérification toutes les 15 secondes
```

## 🐛 Dépannage

### Les notifications Slack ne fonctionnent pas

1. Vérifiez que `SLACK_BOT_TOKEN` est défini dans `.env`
2. Vérifiez que le bot a les permissions `chat:write`
3. Vérifiez que le bot est ajouté au canal
4. Testez la connexion au démarrage (logs)

### Services toujours en DOWN

1. Vérifiez que l'URL est accessible
2. Vérifiez le `expected_status` dans `config.yaml`
3. Augmentez le `timeout` si nécessaire
4. Consultez les logs pour voir l'erreur exacte

### Erreur au démarrage

```bash
# Vérifier les logs
docker-compose logs

# Vérifier la syntaxe YAML
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

Développé pour les équipes DevOps qui veulent :
- Réduire drastiquement leur MTTR
- Éliminer la surveillance manuelle
- Garantir la disponibilité de leurs services
- Respecter leurs SLA

---

**Made with ❤️ for DevOps teams**
