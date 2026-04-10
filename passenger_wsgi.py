import os
import sys
import traceback

# Env: O2switch gaak4328 / logersenegal.com
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')

def application(environ, start_response):
    try:
        from django.core.wsgi import get_wsgi_application
        django_app = get_wsgi_application()
        return django_app(environ, start_response)
    except Exception:
        error_info = traceback.format_exc()
        start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
        return [f"<h1>Erreur de démarrage Django</h1><pre>{error_info}</pre>".encode('utf-8')]
