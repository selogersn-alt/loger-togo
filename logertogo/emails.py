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
        import logging
        logging.getLogger('django').error(f"❌ [SMTP ERROR] Impossible d'envoyer le mail à {to_email}. Erreur : {e}")
        # Fallback : On tente sans BCC admin si c'était activé
        if bcc_admin:
            try:
                email.bcc = []
                return email.send()
            except: pass
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
        import logging
        logging.getLogger('django').error(f"❌ [SMTP ERROR SIMPLE] Erreur envoi à {to_email} : {e}")
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


def send_visit_request_email(owner, user, property, proposed_date):
    """Notifie un propriétaire qu'une visite a été demandée pour son bien."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    dashboard_url = f"{site_url}/mon-compte/"
    
    # Formatage de la date pour l'affichage (si c'est un objet datetime)
    if hasattr(proposed_date, 'strftime'):
        date_str = proposed_date.strftime('%d/%m/%Y à %H:%M')
    else:
        date_str = str(proposed_date)

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:linear-gradient(135deg,#0b4629,#198754);padding:24px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:white;margin:0;">📅 Nouvelle demande de visite</h2>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <p>Bonjour <strong>{owner.first_name or owner.phone_number}</strong>,</p>
        <p>Une nouvelle demande de visite a été effectuée par <strong>{user.get_full_name() or user.phone_number}</strong> pour votre bien :</p>
        <div style="background:#f0fdf4;border-left:4px solid #198754;padding:16px;border-radius:8px;margin:20px 0;">
          <strong style="display:block;margin-bottom:5px;">{property.title}</strong>
          <span style="color:#0b4629;font-weight:bold;">🕒 Date souhaitée : {date_str}</span>
        </div>
        <p>Connectez-vous à votre tableau de bord pour accepter ou reporter ce rendez-vous.</p>
        <p style="text-align:center;margin-top:24px;">
          <a href="{dashboard_url}" style="background:#198754;color:white;padding:12px 28px;border-radius:50px;text-decoration:none;font-weight:bold;display:inline-block;">
            Gérer mes rendez-vous →
          </a>
        </p>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;text-align:center;">Loger Togo · Immobilier de confiance · <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    return send_simple_email(
        f"📅 Demande de visite pour : {property.title}",
        html,
        owner.email
    )


def send_reservation_request_email(owner, user, property, check_in, check_out, total_price):
    """Notifie un propriétaire qu'une demande de réservation a été effectuée sur son bien meublé."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    dashboard_url = f"{site_url}/mon-compte/"
    
    check_in_str = check_in.strftime('%d/%m/%Y') if hasattr(check_in, 'strftime') else str(check_in)
    check_out_str = check_out.strftime('%d/%m/%Y') if hasattr(check_out, 'strftime') else str(check_out)

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:linear-gradient(135deg,#0b4629,#198754);padding:24px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:white;margin:0;">📅 Nouvelle demande de réservation</h2>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <p>Bonjour <strong>{owner.first_name or owner.phone_number}</strong>,</p>
        <p>Une nouvelle demande de réservation a été effectuée par <strong>{user.get_full_name() or user.phone_number}</strong> pour votre bien meublé :</p>
        <div style="background:#f0fdf4;border-left:4px solid #198754;padding:16px;border-radius:8px;margin:20px 0;">
          <strong style="display:block;margin-bottom:5px;">{property.title}</strong>
          <span style="display:block;margin-bottom:5px;color:#0b4629;">📅 Du {check_in_str} au {check_out_str}</span>
          <span style="font-weight:bold;">💵 Prix estimé : {int(total_price):,} FCFA</span>
        </div>
        <p>Connectez-vous à votre tableau de bord Loger Togo pour répondre à cette demande et contacter le client.</p>
        <p style="text-align:center;margin-top:24px;">
          <a href="{dashboard_url}" style="background:#198754;color:white;padding:12px 28px;border-radius:50px;text-decoration:none;font-weight:bold;display:inline-block;">
            Accéder à mon espace →
          </a>
        </p>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;text-align:center;">Loger Togo · Plateforme Immobilière au Togo · <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    return send_simple_email(
        f"📅 Demande de réservation pour : {property.title}",
        html,
        owner.email
    )


# ─── GESTION LOCATIVE ───────────────────────────────────────────────────────

def send_rent_paid_email(payment):
    """Notifie le locataire et le bailleur d'un paiement de loyer."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    lease = payment.lease
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:linear-gradient(135deg,#0b4629,#198754);padding:24px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:white;margin:0;">🧾 Quittance de Loyer</h2>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <p>Bonjour <strong>{lease.tenant.get_full_name()}</strong>,</p>
        <p>Un paiement de loyer a été enregistré pour la période du <strong>{payment.period_start.strftime('%d/%m/%Y')}</strong> au <strong>{payment.period_end.strftime('%d/%m/%Y')}</strong>.</p>
        <div style="background:#f0fdf4;padding:16px;border-radius:8px;text-align:center;margin:20px 0;">
            <span style="display:block;color:#198754;font-size:14px;font-weight:bold;">MONTANT REÇU</span>
            <span style="font-size:28px;font-weight:800;color:#0b4629;">{int(payment.amount_paid):,} FCFA</span>
        </div>
        <p>Vous pouvez télécharger votre quittance de loyer PDF directement sur votre espace locataire.</p>
        <p style="text-align:center;">
          <a href="{site_url}/gestion/locataire/" style="background:#198754;color:white;padding:12px 28px;border-radius:50px;text-decoration:none;font-weight:bold;display:inline-block;">
            Accéder à mon espace →
          </a>
        </p>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;text-align:center;">Loger Togo · Gestion Locative DigitalH · <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    # Envoyer au locataire
    send_simple_email(f"🧾 Paiement reçu - {payment.period_start.strftime('%m/%Y')} | Loger Togo", html, lease.tenant.email)
    # Envoyer copie au bailleur
    send_simple_email(f"🧾 Copie : Paiement enregistré - {lease.tenant.get_full_name()}", html, lease.landlord.email)
    return True


def send_incident_reported_email(incident):
    """Notifie le bailleur d'un nouvel incident signalé."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    lease = incident.lease
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:#dc3545;padding:24px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:white;margin:0;">⚠️ Incident Signalé</h2>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <p>Bonjour <strong>{lease.landlord.get_full_name()}</strong>,</p>
        <p>Un nouvel incident a été signalé par votre locataire <strong>{lease.tenant.get_full_name()}</strong> pour le bien situé à <strong>{lease.property.neighborhood}</strong>.</p>
        <div style="background:#fff5f5;border-left:4px solid #dc3545;padding:16px;border-radius:4px;margin:16px 0;">
          <strong>{incident.title}</strong><br>
          <span style="color:#666;">Priorité : {incident.get_priority_display()}</span>
        </div>
        <p>Connectez-vous à votre tableau de bord pour mettre à jour le statut de l'intervention.</p>
        <p style="text-align:center;">
          <a href="{site_url}/gestion/bailleur/" style="background:#0b4629;color:white;padding:12px 28px;border-radius:50px;text-decoration:none;font-weight:bold;display:inline-block;">
            Gérer les incidents →
          </a>
        </p>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;text-align:center;">Loger Togo · Support Maintenance · <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    return send_simple_email(f"⚠️ Incident : {incident.title} | Loger Togo", html, lease.landlord.email)


def send_incident_status_update_email(incident):
    """Notifie le locataire d'un changement de statut de son incident."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    lease = incident.lease
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:#0d6efd;padding:24px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:white;margin:0;">🔧 Mise à jour maintenance</h2>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <p>Bonjour <strong>{lease.tenant.get_full_name()}</strong>,</p>
        <p>Le statut de votre signalement <strong>"{incident.title}"</strong> a été mis à jour par le bailleur :</p>
        <div style="background:#e7f1ff;padding:16px;border-radius:8px;text-align:center;margin:20px 0;">
            <span style="display:block;color:#0d6efd;font-size:14px;font-weight:bold;">NOUVEAU STATUT</span>
            <span style="font-size:24px;font-weight:800;color:#052c65;">{incident.get_status_display()}</span>
        </div>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;text-align:center;">Loger Togo · Suivi Maintenance · <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    return send_simple_email(f"🔧 Suivi maintenance : {incident.title}", html, lease.tenant.email)

def send_payment_reminder_email(payment):
    """Notifie un locataire que son loyer est impayé."""
    return send_html_email(
        f"⚠️ Rappel : Loyer impayé - {payment.lease.property.title}",
        "emails/payment_reminder.html",
        {'payment': payment, 'tenant': payment.lease.tenant},
        payment.lease.tenant.email
    )


def send_employee_late_notification(manager, employee, minutes, lat=None, lng=None):
    """Notifie un gérant d'hôtel ou d'agence qu'un collaborateur est arrivé en retard."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    maps_link_html = ""
    if lat and lng:
        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        maps_link_html = f"""
        <div style="background:#fff3cd;border:1px solid #ffc107;padding:12px;border-radius:8px;margin:16px 0;text-align:center;">
          <strong>📍 Localisation du Pointage :</strong><br>
          <a href="{maps_url}" target="_blank" style="color:#0b4629;font-weight:bold;text-decoration:underline;">
            Voir la position exacte sur Google Maps →
          </a>
        </div>
        """
    else:
        maps_link_html = """
        <div style="background:#f8d7da;border:1px solid #f5c6cb;color:#721c24;padding:12px;border-radius:8px;margin:16px 0;text-align:center;">
          <strong>⚠️ Télémétrie GPS absente :</strong><br>
          L'employé a désactivé ou refusé la géolocalisation lors de son pointage.
        </div>
        """

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:#dc3545;padding:24px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:white;margin:0;">🚨 Alerte Retard Collaborateur</h2>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <p>Bonjour <strong>{manager.first_name or 'Administrateur'}</strong>,</p>
        <p>Votre collaborateur <strong>{employee.get_full_name()}</strong> vient de pointer son arrivée aujourd'hui avec un retard constaté :</p>
        <div style="background:#f8d7da;color:#721c24;padding:16px;border-radius:8px;text-align:center;margin:20px 0;font-size:18px;">
            <strong>⏱️ RETARD CONSTATED</strong><br>
            <span style="font-size:28px;font-weight:800;">{minutes} minutes</span>
        </div>
        {maps_link_html}
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;text-align:center;">Loger Togo · Suivi RH & Performance · <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    subject = f"🚨 Alerte Retard : {employee.get_full_name()} ({minutes} min)"
    return send_simple_email(subject, html, manager.email)


def send_employee_task_completed_notification(manager, employee, task):
    """Notifie un gérant d'hôtel ou d'agence qu'un collaborateur a validé une consigne."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:#198754;padding:24px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:white;margin:0;">✅ Consigne Terminée</h2>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <p>Bonjour <strong>{manager.first_name or 'Administrateur'}</strong>,</p>
        <p>Votre collaborateur <strong>{employee.get_full_name()}</strong> a marqué la consigne exceptionnelle suivante comme **terminée** :</p>
        <div style="background:#f0fdf4;border-left:4px solid #198754;padding:16px;border-radius:8px;margin:20px 0;">
            <strong style="font-size:16px;color:#0b4629;">{task.title}</strong>
            <p style="margin:8px 0 0 0;color:#555;font-size:14px;">{task.description or 'Aucun détail supplémentaire.'}</p>
        </div>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;text-align:center;">Loger Togo · Suivi RH & Performance · <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    subject = f"✅ Consigne validée par {employee.get_full_name()} : {task.title}"
    return send_simple_email(subject, html, manager.email)


def send_employee_absence_notification(manager, employee, expected_time):
    """Notifie un gérant d'hôtel ou d'agence qu'un collaborateur est absent de son poste (>30 min de retard)."""
    site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
    expected_time_str = expected_time.strftime('%H:%M') if hasattr(expected_time, 'strftime') else str(expected_time)
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
      <div style="background:#dc3545;padding:24px;border-radius:8px 8px 0 0;text-align:center;">
        <h2 style="color:white;margin:0;">🚨 Alerte Absence Poste Collaborateur</h2>
      </div>
      <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
        <p>Bonjour <strong>{manager.first_name or 'Administrateur'}</strong>,</p>
        <p>Votre collaborateur <strong>{employee.get_full_name()}</strong> est actuellement constaté **ABSENT** de son poste de travail :</p>
        <div style="background:#fff5f5;border-left:4px solid #dc3545;padding:16px;border-radius:8px;margin:20px 0;">
            <span style="display:block;color:#dc3545;font-weight:bold;font-size:16px;">⏱️ PRISE DE SERVICE MANQUÉE</span>
            <span style="font-size:14px;color:#555;">Prévue aujourd'hui à : <strong>{expected_time_str}</strong></span>
            <p style="margin:8px 0 0 0;color:#721c24;font-size:13px;font-style:italic;">Aucun pointage d'arrivée n'a été détecté dans les 30 minutes suivant l'heure d'arrivée planifiée.</p>
        </div>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#888;font-size:12px;text-align:center;">Loger Togo · Suivi RH & Performance · <a href="{site_url}" style="color:#198754;">logertogo.com</a></p>
      </div>
    </div>
    """
    subject = f"🚨 Alerte Absence : {employee.get_full_name()} (Non pointé à {expected_time_str})"
    return send_simple_email(subject, html, manager.email)

