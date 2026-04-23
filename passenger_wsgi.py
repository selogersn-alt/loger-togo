import os
import sys

# Ajouter le chemin de l'application au sys.path
path = os.path.dirname(__file__)
if path not in sys.path:
    sys.path.insert(0, path)

# Définir les réglages Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')

# Importer l'application WSGI de Django
# Cela gère automatiquement le django.setup() et le chargement des réglages
try:
    from logertogo.wsgi import application as django_app
except Exception as e:
    # Fallback pour le débogage si le démarrage échoue
    def application(environ, start_response):
        status = '500 Internal Server Error'
        output = f"Erreur de démarrage Django : {str(e)}".encode('utf-8')
        response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]
else:
    # Point d'entrée Passenger standard
    application = django_app
