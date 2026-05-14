# ═══════════════════════════════════════════════════════════
# Loger Togo — Dockerfile Production FINAL (Hetzner VPS)
# 
# Corrections :
#  1. HOME valide pour Gunicorn (évite /nonexistent)
#  2. staticfiles pre-créé et owned par django AVANT mount
#  3. Scripts run-time via entrypoint robuste
# ═══════════════════════════════════════════════════════════
FROM python:3.13-slim

# Empêcher Python d'écrire des fichiers .pyc et activer le mode non bufferisé
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Fix Gunicorn "Permission denied: /nonexistent" — définir un HOME valide
ENV HOME=/home/django

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
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet complet
COPY . /app/

# Copier et rendre le script entrypoint exécutable
COPY ./scripts/entrypoint.sh /scripts/entrypoint.sh
RUN chmod +x /scripts/entrypoint.sh

# ── CORRECTION PERMISSIONS ─────────────────────────────────
# UID 999 correspond au chown dans docker-compose fixer service
RUN addgroup --system --gid 999 django \
    && adduser --system --ingroup django --uid 999 --home /home/django --shell /bin/sh django

# Créer tous les dossiers et appliquer les permissions
RUN mkdir -p /app/staticfiles /app/media /home/django /scripts \
    && chown -R django:django /app /scripts /home/django

# Exposer le port par défaut de Gunicorn
EXPOSE 8000

# Basculer sur l'utilisateur non-root
USER django

# Point d'entrée
ENTRYPOINT ["/scripts/entrypoint.sh"]
