from django.http import HttpResponse
from solvable.models import IncidentReport
from django.db.models import Sum
from logersn.models import Property
import traceback

def debug_view(request):
    try:
        # Tente de forcer l'évaluation de tout ce que fait home_view
        from logersenegal.views import home_view
        response = home_view(request)
        # Force l'évaluation du template (rendu lazy)
        content = response.render()
        return response
    except Exception:
        error_info = traceback.format_exc()
        return HttpResponse(f"<h1>ERREUR TROUVEE</h1><pre>{error_info}</pre>")
