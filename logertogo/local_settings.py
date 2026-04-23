DEBUG = True
ALLOWED_HOSTS = ['*']

import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# TERMII SMS API
TERMII_API_KEY = "TLgPLfhEIJlbVRoAXHfRoGJZGLntoUdrFuQzSJhXWHYfujUfSHuTMtlNiISWqj"
TERMII_SENDER_ID = "Loger Togo"  # En attente d'approbation chez Termii
