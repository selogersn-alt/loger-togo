# Utiliser une image Python officielle légère
FROM python:3.13-slim

# Empêcher Python d'écrire des fichiers .pyc et activer le mode non bufferisé
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    libcairo2-dev \
    pkg-config \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet
COPY . /app/

# Donner les permissions d'exécution au script de démarrage
COPY ./scripts/entrypoint.sh /scripts/entrypoint.sh
RUN chmod +x /scripts/entrypoint.sh

# Création d'un utilisateur non-root pour la sécurité en production
RUN addgroup --system django && adduser --system --ingroup django django
RUN chown -R django:django /app /scripts

# Exposer le port par défaut de Gunicorn
EXPOSE 8000

# Basculer sur l'utilisateur non-root
USER django

# Utiliser le script entrypoint
ENTRYPOINT ["/scripts/entrypoint.sh"]
