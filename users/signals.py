from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import KYCProfile

@receiver(post_save, sender=KYCProfile)
def process_kyc_approval(sender, instance, **kwargs):
    # Loger Togo : Plus de profil NILS automatique. 
    # On garde le signal pour d'éventuelles actions futures sur l'approbation KYC.
    pass
