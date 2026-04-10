from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_html_email(subject, template_name, context, to_email, bcc_admin=True):
    """Envoie un e-mail HTML stylisé avec Fallback texte et copie cachée admin."""
    if not to_email:
        return False
        
    context['site_url'] = getattr(settings, 'SITE_URL', 'https://logersenegal.com')
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)
    
    bcc = [settings.DEFAULT_FROM_EMAIL] if bcc_admin else []
    
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        bcc=bcc
    )
    email.attach_alternative(html_content, "text/html")
    try:
        return email.send()
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False

def send_otp_email(user, otp_code):
    """Envoie le code OTP par email (Pas de copie admin pour la confidentialité)."""
    return send_html_email(
        "Votre code de vérification - Loger Sénégal",
        "emails/otp_email.html",
        {'user': user, 'otp_code': otp_code},
        user.email,
        bcc_admin=False
    )

def send_property_published_email(user, property):
    """Notification de publication d'annonce."""
    return send_html_email(
        "Félicitations ! Votre annonce est en ligne",
        "emails/property_published.html",
        {'user': user, 'property': property},
        user.email
    )

def send_doc_submitted_email(user):
    """Confirmation de réception de documents."""
    return send_html_email(
        "Documents bien reçus - Solvable LogerSN",
        "emails/doc_submitted.html",
        {'user': user},
        user.email
    )
