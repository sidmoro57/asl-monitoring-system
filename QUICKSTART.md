# 🚀 Guide de Démarrage Rapide - ASL Monitoring

Ce guide vous aidera à mettre en place le système de monitoring ASL en moins de 5 minutes.

## Étape 1: Prérequis

Assurez-vous d'avoir:
- **Docker** et **Docker Compose** installés OU **Python 3.11+**
- Un **workspace Slack** (optionnel mais recommandé pour les alertes)

## Étape 2: Configuration Slack (Optionnel mais Recommandé)

### 2.1 Créer une Application Slack

1. Allez sur https://api.slack.com/apps
2. Cliquez sur **"Create New App"** → **"From scratch"**
3. Nommez votre app (ex: "ASL Monitor") et sélectionnez votre workspace
4. Cliquez sur **"Create App"**

### 2.2 Configurer les Permissions

1. Dans le menu latéral, cliquez sur **"OAuth & Permissions"**
2. Descendez à **"Scopes"** → **"Bot Token Scopes"**
3. Ajoutez ces permissions:
   - `chat:write` - Pour envoyer des messages
   - `chat:write.public` - Pour poster dans les canaux publics
4. Remontez et cliquez sur **"Install to Workspace"**
5. Autorisez l'application
6. **Copiez le "Bot User OAuth Token"** (commence par `xoxb-`)

### 2.3 Ajouter le Bot à votre Canal

1. Ouvrez Slack
2. Allez dans le canal où vous voulez recevoir les alertes (ex: `#asl-alerts`)
3. Tapez `/invite @ASL Monitor` (remplacez par le nom de votre bot)

## Étape 3: Déploiement

### Option A: Avec Docker (Recommandé)

```bash
# 1. Cloner le repository
git clone https://github.com/sidmoro57/asl-monitoring-system.git
cd asl-monitoring-system

# 2. Créer le fichier .env avec votre token Slack
echo "SLACK_BOT_TOKEN=xoxb-votre-token-ici" > .env

# 3. Éditer config.yaml et définir vos services
nano config.yaml  # ou vim, code, etc.

# 4. Démarrer le monitoring
docker-compose up -d

# 5. Vérifier les logs
docker-compose logs -f
```

### Option B: Avec Python

```bash
# 1. Cloner et installer
git clone https://github.com/sidmoro57/asl-monitoring-system.git
cd asl-monitoring-system
pip install -r requirements.txt

# 2. Configuration
echo "SLACK_BOT_TOKEN=xoxb-votre-token-ici" > .env

# 3. Éditer config.yaml
nano config.yaml

# 4. Lancer
python asl_monitor.py
```

## Étape 4: Configuration des Services

Éditez `config.yaml` pour ajouter vos services à monitorer:

```yaml
services:
  - name: "Mon API Production"
    url: "https://api.monsite.com/health"
    method: "GET"
    expected_status: 200
    timeout: 10
    critical: true
    
  - name: "Mon Application Web"
    url: "https://app.monsite.com/health"
    method: "GET"
    expected_status: 200
    timeout: 10
    critical: true
```

### Paramètres Expliqués

- **name**: Nom du service (affiché dans les alertes)
- **url**: URL du endpoint de health check
- **method**: Méthode HTTP (GET, POST, etc.)
- **expected_status**: Code HTTP attendu pour considérer le service UP (généralement 200)
- **timeout**: Timeout en secondes avant de considérer le service DOWN
- **critical**: `true` = mention @channel dans Slack, `false` = alerte simple

## Étape 5: Configuration du Monitoring

Ajustez les paramètres de monitoring selon vos besoins:

```yaml
monitoring:
  check_interval: 20          # Vérification toutes les 20 secondes
  failure_threshold: 2        # 2 échecs consécutifs avant alerte
  default_timeout: 10         # Timeout par défaut en secondes

slack:
  channel: "#asl-alerts"      # Canal pour les notifications
  enabled: true               # Activer/désactiver Slack
  mention_channel: true       # Mentionner @channel pour services critiques
```

## Étape 6: Vérification

### Vérifier que tout fonctionne

1. **Vérifier les logs**:
   ```bash
   # Docker
   docker-compose logs -f
   
   # Python
   tail -f logs/monitoring.log
   ```

2. **Vous devriez voir**:
   ```
   🚀 DÉMARRAGE DU SERVICE DE MONITORING ASL
   Services surveillés: 2
   Intervalle de vérification: 20s
   Seuil d'échecs: 2
   Notifications Slack: ✓ Activées
   ✓ Connexion Slack OK - Bot: ASL Monitor
   ```

3. **Vérifier le statut**:
   ```bash
   [2024-11-06 10:30:00] Status: 2 UP / 0 DOWN
   ```

### Tester une Alerte

Pour vérifier que les alertes fonctionnent:

1. Ajoutez temporairement un service avec une URL invalide:
   ```yaml
   - name: "Test Alert"
     url: "https://invalid-url-test-12345.com/health"
     critical: true
   ```

2. Redémarrez:
   ```bash
   docker-compose restart  # Docker
   # OU
   # Ctrl+C puis relancer python asl_monitor.py
   ```

3. Attendez ~40 secondes (2 échecs × 20s)
4. Vous devriez recevoir une alerte dans Slack! 🚨

## Commandes Utiles

### Docker

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Voir les logs en temps réel
docker-compose logs -f

# Redémarrer après modification de config.yaml
docker-compose restart

# Voir les statistiques
docker stats asl-monitoring
```

### Gestion des Logs

```bash
# Voir les logs de monitoring
tail -f logs/monitoring.log

# Voir les incidents
ls incidents/
cat incidents/API_Production_20241106_153045.json
```

## Dépannage Rapide

### "Slack notifications disabled"

➡️ Vérifiez que `SLACK_BOT_TOKEN` est défini dans `.env`

### "Service always DOWN"

➡️ Vérifiez:
1. L'URL est accessible: `curl https://votre-url/health`
2. Le `expected_status` correspond à la réponse
3. Augmentez le `timeout` si nécessaire

### "Permission denied" sur Docker

➡️ Lancez avec sudo ou ajoutez votre utilisateur au groupe docker:
```bash
sudo usermod -aG docker $USER
```

## Prochaines Étapes

✅ Système opérationnel - Félicitations! 🎉

Maintenant vous pouvez:

1. **Personnaliser les alertes** - Ajoutez plus de services dans `config.yaml`
2. **Consulter l'historique** - Explorez le dossier `incidents/`
3. **Ajuster le timing** - Modifiez `check_interval` selon vos besoins
4. **Monitorer les métriques** - Consultez les logs pour les statistiques

## Support

Besoin d'aide? 
- 📖 Documentation complète: [README.md](README.md)
- 🐛 Reporter un bug: [GitHub Issues](https://github.com/sidmoro57/asl-monitoring-system/issues)

---

**Profitez d'un monitoring proactif! 🚀**
