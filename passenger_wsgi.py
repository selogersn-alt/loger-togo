import os
import sys

# Env: O2switch gaak4328 / loger_app
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
