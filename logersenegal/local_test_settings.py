from .settings import *

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'logersenegal.com', 'www.logersenegal.com', 'solvable-sn.onrender.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Désactiver la vérification MySQL au démarrage pour les tests SQLite
import pymysql
pymysql.install_as_MySQLdb = lambda: None
