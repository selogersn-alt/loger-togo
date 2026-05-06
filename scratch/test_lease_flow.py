import os
import django
import sys

# Setup Django
sys.path.append('d:/HDIGITAL/ANDROID_ANTIGRAVITY/LOGERTOGO')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from users.models import User
from logersn.models import Property
from management.models import Lease
from management.utils import render_to_pdf
from django.core.files.base import ContentFile
from django.utils import timezone
import datetime

def test_flow():
    print("--- DÉBUT DU TEST DE FLUX DE BAIL ---")
    
    # 1. Créer un bailleur avec logo
    landlord, _ = User.objects.get_or_create(
        phone_number="+22899112233",
        defaults={
            'first_name': 'Agence',
            'last_name': 'DigitalH',
            'company_name': 'DigitalH Real Estate',
            'role': 'LANDLORD',
            'email': 'contact@digitalh.com'
        }
    )
    print(f"Bailleur créé: {landlord}")

    # 2. Créer un locataire
    tenant, _ = User.objects.get_or_create(
        phone_number="+22899000000",
        defaults={
            'first_name': 'Koffi',
            'last_name': 'Test',
            'role': 'TENANT'
        }
    )
    print(f"Locataire créé: {tenant}")

    # 3. Créer une propriété
    prop, _ = Property.objects.get_or_create(
        owner=landlord,
        title="Appartement de Luxe à Agoé",
        defaults={
            'description': 'Superbe appartement 3 pièces.',
            'price': 150000,
            'city': 'Lomé',
            'neighborhood': 'Agoé',
            'property_type': 'APARTMENT',
            'listing_category': 'RENT'
        }
    )
    print(f"Propriété créée: {prop}")

    # 4. Créer un bail avec personnalisation
    lease = Lease.objects.create(
        property=prop,
        tenant=tenant,
        landlord=landlord,
        start_date=timezone.now().date(),
        rent_amount=150000,
        deposit_amount=300000,
        custom_header_text="AGENCE DIGITALE H - LOMÉ",
        custom_contract_terms="1. Interdiction de sous-louer.\n2. Animaux non autorisés.\n3. Entretien de la climatisation à charge du locataire.",
        status='ACTIVE'
    )
    print(f"Bail créé avec ID: {lease.id}")

    # 5. Tester la génération du PDF
    print("Génération du PDF du contrat...")
    context = {
        'lease': lease,
        'today': timezone.now().date()
    }
    pdf = render_to_pdf('management/pdf/lease_contract.html', context)
    
    if pdf:
        print("SUCCES: PDF genere avec succes !")
        # On sauvegarde le PDF pour vérification manuelle si besoin
        filename = f"test_contract_{lease.id}.pdf"
        lease.contract_pdf.save(filename, ContentFile(pdf.content))
        print(f"Fichier sauvegardé dans: {lease.contract_pdf.url}")
    else:
        print("❌ Erreur: Échec de la génération du PDF.")

    print("--- FIN DU TEST ---")

if __name__ == "__main__":
    test_flow()
