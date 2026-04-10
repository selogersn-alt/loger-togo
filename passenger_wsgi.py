import os
import sys
import traceback

# Env: O2switch gaak4328 / logersenegal.com
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')

def application(environ, start_response):
    log_file = os.path.join(os.path.dirname(__file__), 'debug_error.log')
    try:
        from logersenegal.wsgi import application as django_app
        return django_app(environ, start_response)
    except Exception:
        error_info = traceback.format_exc()
        with open(log_file, 'a') as f:
            f.write("\n--- NEW ERROR ---\n")
            f.write(error_info)
        
        start_response('500 Internal Server Error', [('Content-Type', 'text/html; charset=utf-8')])
        return [f"<h1>Erreur Critique Detectee</h1><p>Consultez le fichier <b>debug_error.log</b> a la racine pour le detail.</p><pre>{error_info}</pre>".encode('utf-8')]
