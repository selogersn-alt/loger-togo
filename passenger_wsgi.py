import os
import sys
import traceback

# Env: O2switch gaak4328 / loger_app
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')

def application(environ, start_response):
    with open('debug_passenger.log', 'a') as f:
        f.write(f"Application start requested at {os.environ.get('REQUEST_URI', 'unknown')}\n")
    try:
        from logersenegal.wsgi import application as django_app
        return django_app(environ, start_response)
    except Exception as e:
        import traceback
        error_info = traceback.format_exc()
        with open('debug_passenger.log', 'a') as f:
            f.write(f"Error caught: {error_info}\n")
        start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
        return [f"<h1>Traceback d'Erreur</h1><pre>{error_info}</pre>".encode('utf-8')]
