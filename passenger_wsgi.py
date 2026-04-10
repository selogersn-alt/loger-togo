import os
import sys
import traceback

def log_debug(msg):
    with open(os.path.join(os.path.dirname(__file__), 'debug_global.log'), 'a') as f:
        f.write(f"--- {msg} ---\n")

try:
    sys.path.insert(0, os.path.dirname(__file__))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')
    import django
    django.setup()
    from django.core.wsgi import get_wsgi_application
    django_instance = get_wsgi_application()
    log_debug("GLOBAL: Django instance created")
except Exception as e:
    log_debug(f"GLOBAL ERROR: {traceback.format_exc()}")

def application(environ, start_response):
    log_debug("APP: application() called")
    try:
        log_debug("APP: Calling django_instance")
        response = django_instance(environ, start_response)
        log_debug("APP: Iterating response")
        return [chunk for chunk in response]
    except Exception:
        error_info = traceback.format_exc()
        log_debug(f"APP ERROR: {error_info}")
        start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
        return [f"<h1>Erreur Detective</h1><pre>{error_info}</pre>".encode('utf-8')]
