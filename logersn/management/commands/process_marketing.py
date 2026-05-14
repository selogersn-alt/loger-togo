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
            from users.models import User
            users = User.objects.filter(is_active=True).exclude(email__isnull=True).exclude(email='')
            
            if campaign.recipient_group == 'AGENTS':
                users = users.filter(role__in=['AGENCY', 'BROKER', 'AGENT'])
            elif campaign.recipient_group == 'OWNERS':
                users = users.filter(role='LANDLORD')
            elif campaign.recipient_group == 'TENANTS':
                users = users.filter(role='TENANT')
            elif campaign.recipient_group == 'VERIFIED':
                users = users.filter(is_verified_pro=True)
            elif campaign.recipient_group == 'ALL':
                pass # Already got all active users with email
            
            # Combiner avec les destinataires individuels
            if campaign.individual_recipients.exists():
                users = (users | campaign.individual_recipients.all()).distinct()

            count = 0
            from logertogo.emails import send_simple_email
            
            for user in users:
                # Personnalisation
                first_name = user.first_name or "Client"
                last_name = user.last_name or ""
                user_content = campaign.content.replace('[PRENOM]', first_name).replace('[NOM]', last_name)
                
                if send_simple_email(campaign.subject, user_content, user.email):
                    count += 1

            campaign.is_sent = True
            campaign.sent_at = now
            campaign.save()
            self.stdout.write(self.style.SUCCESS(f"Campagne '{campaign.subject}' envoyée avec succès à {count} personnes."))
