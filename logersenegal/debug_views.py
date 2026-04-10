from django.http import HttpResponse
from solvable.models import IncidentReport

def debug_view(request):
    try:
        count = IncidentReport.objects.count()
        return HttpResponse(f"<h1>Debug Mode: OK</h1><p>Connexion BDD OK. Nombre d'incidents : {count}</p>")
    except Exception as e:
        import traceback
        return HttpResponse(f"<h1>Erreur BDD</h1><pre>{traceback.format_exc()}</pre>")
