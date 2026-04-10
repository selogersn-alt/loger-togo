import os
import sys
import traceback

# RESET DU LOG POUR ETRE SUR DE CE QU'ON VOIT
with open(os.path.join(os.path.dirname(__file__), 'debug_global.log'), 'w') as f:
    f.write(f"--- RESTART LOG {os.getcwd()} ---\n")

def log_debug(msg):
    with open(os.path.join(os.path.dirname(__file__), 'debug_global.log'), 'a') as f:
        f.write(f"--- {msg} ---\n")

try:
    log_debug("GLOBAL: Setting up sys.path")
    sys.path.insert(0, os.path.dirname(__file__))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')
    
    log_debug("GLOBAL: django.setup()")
    import django
    django.setup()
    
    log_debug("GLOBAL: get_wsgi_application()")
    from django.core.wsgi import get_wsgi_application
    django_instance = get_wsgi_application()
    log_debug("GLOBAL: Instance OK")
except Exception as e:
    log_debug(f"GLOBAL ERROR: {traceback.format_exc()}")

def application(environ, start_response):
    log_debug("APP: application() called")
    try:
        response = django_instance(environ, start_response)
        return [chunk for chunk in response]
    except Exception:
        error_info = traceback.format_exc()
        log_debug(f"APP ERROR: {error_info}")
        start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
        return [f"<h1>Erreur Detective</h1><pre>{error_info}</pre>".encode('utf-8')]
