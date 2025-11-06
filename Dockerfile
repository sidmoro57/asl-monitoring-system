FROM python:3.11-slim

WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY *.py .
COPY config.yaml .

# Créer les répertoires nécessaires
RUN mkdir -p logs incidents

# Définir les variables d'environnement par défaut
ENV PYTHONUNBUFFERED=1

# Lancer le service de monitoring
CMD ["python", "asl_monitor.py"]
