from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm

def generate_receipt_pdf(payment):
    """Génère un PDF en mémoire (BytesIO) pour une quittance de loyer"""
    buffer = BytesIO()
    
    # Configuration du document A4
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # En-tête (Logo / Nom de l'app)
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.HexColor("#083820"))
    c.drawString(2 * cm, height - 3 * cm, "SOLVABLE")
    
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.gray)
    c.drawString(2 * cm, height - 3.7 * cm, "Garantie de confiance immobilière")
    
    # Titre du document
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2.0, height - 6 * cm, "QUITTANCE DE LOYER")
    
    # Ligne de séparation
    c.setStrokeColor(colors.HexColor("#7fd47d"))
    c.setLineWidth(2)
    c.line(2 * cm, height - 6.5 * cm, width - 2 * cm, height - 6.5 * cm)
    
    # Informations
    filiation = payment.rental_filiation
    tenant = filiation.tenant
    landlord = filiation.landlord
    property_obj = filiation.property
    
    locataire_name = f"{tenant.first_name} {tenant.last_name}" if tenant.first_name else tenant.email
    bailleur_name = f"{landlord.first_name} {landlord.last_name}" if landlord.first_name else (landlord.company_name or landlord.email)
    
    text_y = height - 8 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, text_y, "Bailleur / Propriétaire :")
    c.setFont("Helvetica", 12)
    c.drawString(7 * cm, text_y, bailleur_name)
    
    text_y -= 1 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, text_y, "Locataire :")
    c.setFont("Helvetica", 12)
    c.drawString(7 * cm, text_y, locataire_name)
    
    text_y -= 1 * cm
    if tenant.nils_profile:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, text_y, "Numéro NILS :")
        c.setFont("Helvetica", 12)
        c.drawString(7 * cm, text_y, tenant.nils_profile.nils_number)
    
    text_y -= 1.5 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, text_y, "Adresse du bien :")
    c.setFont("Helvetica", 12)
    prop_addr = property_obj.title if property_obj else "Propriété enregistrée"
    c.drawString(7 * cm, text_y, prop_addr[:50])
    
    text_y -= 2 * cm
    c.setFillColor(colors.HexColor("#f8f9fa"))
    c.rect(2 * cm, text_y - 1 * cm, width - 4 * cm, 2.5 * cm, fill=1, stroke=0)
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2.5 * cm, text_y + 0.5 * cm, "Mois / Année :")
    c.setFont("Helvetica", 12)
    c.drawString(6 * cm, text_y + 0.5 * cm, payment.month_year.strftime('%B %Y') if payment.month_year else "N/A")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2.5 * cm, text_y - 0.5 * cm, "Montant payé :")
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor("#083820"))
    c.drawString(6 * cm, text_y - 0.5 * cm, f"{filiation.monthly_rent} FCFA")
    
    # Bas de page
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    text_bottom = 4 * cm
    c.drawString(2 * cm, text_bottom, f"Fait le {payment.payment_date.strftime('%d/%m/%Y') if payment.payment_date else payment.created_at.strftime('%d/%m/%Y')} via la plateforme Solvable.")
    c.drawString(2 * cm, text_bottom - 0.5 * cm, "Cette quittance annule tout reçu donné précédemment pour ce même mois.")
    
    c.setStrokeColor(colors.lightgrey)
    c.line(2 * cm, 2 * cm, width - 2 * cm, 2 * cm)
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width / 2.0, 1.5 * cm, "Document généré électroniquement par Solvable - Loger Togo")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer
