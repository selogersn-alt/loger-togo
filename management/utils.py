import io
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os

def render_to_pdf(template_src, context_dict={}):
    """
    Rendu d'un template HTML en fichier PDF.
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    
    # Création du PDF
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("utf-8")), result)
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
