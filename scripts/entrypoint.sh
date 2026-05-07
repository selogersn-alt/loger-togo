#!/bin/sh
set -e

echo "═══════════════════════════════════════════════════"
echo "   Loger Togo — Démarrage Production (Hetzner VPS)"
echo "═══════════════════════════════════════════════════"

# ─── 1. Attendre que PostgreSQL soit prêt ─────────────────
echo "[1/5] Attente de la base de données PostgreSQL..."
sleep 3

# ─── 2. Appliquer les migrations ──────────────────────────
echo "[2/5] Application des migrations..."
python manage.py migrate --noinput

# ─── 3. Collecter les fichiers statiques ──────────────────
echo "[3/5] Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear 2>&1 | tail -5
echo "    → Statiques collectés avec succès."

# ─── 4. Compilation des traductions (non-bloquant) ────────
echo "[4/5] Compilation des traductions..."
python manage.py compilemessages 2>/dev/null || echo "    ⚠ Traductions non compilées (locales absentes - ignoré)"

# ─── 5. Démarrage de Gunicorn ─────────────────────────────
echo "[5/5] Démarrage du serveur Gunicorn..."
echo "    → Workers: 3 | Port: 8000 | Timeout: 120s"

exec gunicorn logertogo.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class sync \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
