import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from logersn.models import MarketingCampaign

class Command(BaseCommand):
    help = "Envoie les campagnes marketing planifiées qui sont prêtes."

    def handle(self, *args, **options):
        now = timezone.now()
        pending_campaigns = MarketingCampaign.objects.filter(
            is_sent=False,
            scheduled_for__lte=now
        )

        if not pending_campaigns.exists():
            self.stdout.write("Aucune campagne planifiée à envoyer.")
            return

        for campaign in pending_campaigns:
            self.stdout.write(f"Traitement de la campagne : {campaign.subject}")
            
            # Détermination des destinataires
            recipients = []
            if campaign.individual_recipients.exists():
                recipients = campaign.individual_recipients.all()
            else:
                from users.models import User
                if campaign.recipient_group == 'ALL':
                    recipients = User.objects.filter(is_active=True)
                elif campaign.recipient_group == 'AGENTS':
                    recipients = User.objects.filter(role__in=['AGENCY', 'BROKER', 'AGENT'])
                # ... autres groupes si nécessaire

            count = 0
            for user in recipients:
                if user.email:
                    # Personnalisation
                    user_content = campaign.content.replace('[PRENOM]', user.first_name or "").replace('[NOM]', user.last_name or "")
                    
                    email = EmailMultiAlternatives(
                        subject=campaign.subject,
                        body="HTML needed",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[user.email]
                    )
                    html_content = render_to_string('emails/base_email.html', {
                        'content': user_content,
                        'site_url': 'https://logertogo.com'
                    })
                    email.attach_alternative(html_content, "text/html")
                    
                    try:
                        email.send()
                        count += 1
                    except Exception as e:
                        self.stderr.write(f"Erreur d'envoi à {user.email}: {e}")

            campaign.is_sent = True
            campaign.sent_at = now
            campaign.save()
            self.stdout.write(self.style.SUCCESS(f"Campagne '{campaign.subject}' envoyée avec succès à {count} personnes."))
