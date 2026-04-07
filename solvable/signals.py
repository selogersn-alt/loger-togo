from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PaymentHistory, IncidentReport

@receiver(post_save, sender=PaymentHistory)
@receiver(post_delete, sender=PaymentHistory)
def update_nils_on_payment_change(sender, instance, **kwargs):
    if instance.rental_filiation and instance.rental_filiation.tenant:
        tenant = instance.rental_filiation.tenant
        # DigitalH Audit Fix: check if property returns a valid profile
        profile = getattr(tenant, 'nils_profile', None)
        if profile:
            profile.update_score()

@receiver(post_save, sender=IncidentReport)
@receiver(post_delete, sender=IncidentReport)
def update_nils_on_incident_change(sender, instance, **kwargs):
    if instance.reported_tenant:
        reported_tenant = instance.reported_tenant
        # DigitalH Audit Fix: check if property returns a valid profile
        profile = getattr(reported_tenant, 'nils_profile', None)
        if profile:
            profile.update_score()

from .models import RentalFiliation
@receiver(post_save, sender=RentalFiliation)
def update_nils_on_filiation_change(sender, instance, **kwargs):
    """Updates score when a filiation rating is added or status changes."""
    t_profile = getattr(instance.tenant, 'nils_profile', None) if instance.tenant else None
    if t_profile:
        t_profile.update_score()
        
    l_profile = getattr(instance.landlord, 'nils_profile', None) if instance.landlord else None
    if l_profile:
        l_profile.update_score()
