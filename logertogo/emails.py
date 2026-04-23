from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_html_email(subject, template_name, context, to_email, bcc_admin=True):
    """Envoie un e-mail HTML stylisé avec fallback texte et copie cachée admin."""
    if not to_email:
        return False
    context['site_url'] = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    try:
        html_content = render_to_string(template_name, context)
    except Exception:
        html_content = f"<p>{subject}</p>"
    text_content = strip_tags(html_content)
    bcc = [settings.SERVER_EMAIL] if bcc_admin else []
    email = EmailMultiAlternatives(
        subject, text_content, settings.DEFAULT_FROM_EMAIL, [to_email], bcc=bcc
    )
    email.attach_alternative(html_content, "text/html")
    try:
        return email.send()
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


def send_simple_email(subject, message_html, to_email):
    """Envoi simple sans template (inline HTML)."""
    if not to_email:
        return False
    text = strip_tags(message_html)
    email = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [to_email])
    email.attach_alternative(message_html, "text/html")
    try:
        return email.send()
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


# ─── EXISTANTS ──────────────────────────────────────────────────────────────

def send_otp_email(user, otp_code):
    """Code OTP de vérification de compte."""
    return send_html_email(
        "Votre code de vérification - Loger Togo",
        "emails/otp_email.html",
        {'user': user, 'otp_code': otp_code},
        user.email,
        bcc_admin=False
    )


def send_property_published_email(user, property):
    """Notification : annonce publiée par l'admin."""
    return send_html_email(
        "✅ Votre annonce est en ligne sur Loger Togo !",
        "emails/property_published.html",
        {'user': user, 'property': property},
        user.email
    )


def send_password_reset_email(user, reset_url):
    """Lien de réinitialisation de mot de passe."""
    return send_html_email(
        "Réinitialisation de votre mot de passe - Loger Togo",
        "emails/password_reset.html",
        {'user': user, 'reset_url': reset_url},
        user.email,
        bcc_admin=False
    )


# ─── NOUVEAUX ───────────────────────────────────────────────────────────────

def send_new_message_notification(recipient, sender, conversation, message_preview):
    """Notifie un utilisateur qu'il a reçu un nouveau message."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    dashboard_url = f"{site_url}/mon-compte/?tab=messages&conv={conversation.id}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:linear-gradient(135deg,#0b4629,#198754);padding:24px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:white;margin:0;">💬 Nouveau message</h2>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <p>Bonjour <strong>{recipient.first_name or recipient.phone_number}</strong>,</p>
        <p>Vous avez reçu un nouveau message de <strong>{sender.get_full_name() or sender.phone_number}</strong> :</p>
        <div style="background:#f0fdf4;border-left:4px solid #198754;padding:16px;border-radius:4px;margin:16px 0;font-style:italic;">
          "{message_preview}"
        </div>
        <p style="text-align:center;">
          <a href="{dashboard_url}" style="background:#198754;color:white;padding:12px 28px;border-radius:50px;text-decoration:none;font-weight:bold;display:inline-block;">
            Répondre maintenant →
          </a>
        </p>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;text-align:center;">Loger Togo · <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    return send_simple_email(
        f"💬 Nouveau message de {sender.get_full_name() or sender.phone_number}",
        html,
        recipient.email
    )


def send_property_pending_email(owner, property):
    """Notifie le propriétaire que son annonce est en attente de validation."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:linear-gradient(135deg,#0b4629,#198754);padding:24px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:white;margin:0;">🏠 Annonce reçue !</h2>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <p>Bonjour <strong>{owner.first_name or owner.phone_number}</strong>,</p>
        <p>Nous avons bien reçu votre annonce : <strong>"{property.title}"</strong></p>
        <p>Elle est actuellement en cours de vérification par notre équipe. Vous serez notifié(e) par email dès sa validation.</p>
        <div style="background:#fff3cd;border:1px solid #ffc107;padding:12px;border-radius:8px;margin:16px 0;">
          <strong>⏳ Délai habituel :</strong> 24h à 48h (jours ouvrables)
        </div>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;text-align:center;">Loger Togo · <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    return send_simple_email(
        "✅ Annonce reçue – En attente de validation | Loger Togo",
        html,
        owner.email
    )


def send_new_property_alert(subscribers, property):
    """Alerte : nouvelle annonce publiée dans une ville (liste d'emails)."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    prop_url = f"{site_url}{property.get_absolute_url()}"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:linear-gradient(135deg,#0b4629,#198754);padding:24px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:white;margin:0;">🏡 Nouvelle annonce à {property.city}</h2>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <h3 style="color:#0b4629;">{property.title}</h3>
        <p><strong>Type :</strong> {property.get_property_type_display()} · <strong>Prix :</strong> {int(property.price):,} FCFA/mois</p>
        <p><strong>Localisation :</strong> {property.neighborhood}, {property.city}</p>
        <p style="text-align:center;margin-top:20px;">
          <a href="{prop_url}" style="background:#f5c42f;color:#0b4629;padding:12px 28px;border-radius:50px;text-decoration:none;font-weight:bold;display:inline-block;">
            Voir l'annonce →
          </a>
        </p>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:11px;text-align:center;">Vous recevez cet email car vous avez demandé des alertes immobilières. <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    count = 0
    for email in subscribers:
        if send_simple_email(f"🏡 Nouvelle annonce : {property.title} | Loger Togo", html, email):
            count += 1
    return count


def send_review_notification(owner, reviewer, property, rating):
    """Notifie un bailleur qu'il a reçu un avis."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    stars = "⭐" * rating
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:linear-gradient(135deg,#0b4629,#198754);padding:24px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:white;margin:0;">{stars} Nouvel avis reçu</h2>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <p>Bonjour <strong>{owner.first_name or owner.phone_number}</strong>,</p>
        <p><strong>{reviewer.get_full_name() or reviewer.phone_number}</strong> a laissé un avis {stars} sur votre annonce :</p>
        <p><strong>"{property.title}"</strong></p>
        <p style="text-align:center;margin-top:20px;">
          <a href="{site_url}{property.get_absolute_url()}" style="background:#198754;color:white;padding:12px 28px;border-radius:50px;text-decoration:none;font-weight:bold;display:inline-block;">
            Voir l'avis →
          </a>
        </p>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;text-align:center;">Loger Togo · <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    return send_simple_email(f"{stars} Nouvel avis sur votre annonce | Loger Togo", html, owner.email)


def send_account_created_email(user):
    """Email de bienvenue à l'inscription."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:linear-gradient(135deg,#0b4629,#198754);padding:32px;border-radius:8px 8px 0 0;text-align:center;">
        <h1 style="color:white;margin:0;">🎉 Bienvenue sur Loger Togo !</h1>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <p>Bonjour <strong>{user.first_name or user.phone_number}</strong>,</p>
        <p>Votre compte a été créé avec succès. Vous pouvez maintenant :</p>
        <ul style="line-height:2;">
          <li>🔍 Parcourir les annonces immobilières au Togo</li>
          <li>❤️ Sauvegarder vos biens favoris</li>
          <li>💬 Contacter les propriétaires directement</li>
          <li>🏠 Publier vos propres annonces</li>
        </ul>
        <p style="text-align:center;margin-top:24px;">
          <a href="{site_url}/annonces/" style="background:#f5c42f;color:#0b4629;padding:12px 28px;border-radius:50px;text-decoration:none;font-weight:bold;display:inline-block;">
            Découvrir les annonces →
          </a>
        </p>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;text-align:center;">Loger Togo · Votre immobilier de confiance au Togo · <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    return send_simple_email("🎉 Bienvenue sur Loger Togo !", html, user.email)
