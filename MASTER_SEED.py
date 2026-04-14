import os
import django
import uuid
from decimal import Decimal
from django.utils import timezone
import datetime

# Configuration Django pour le serveur O2switch
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')
django.setup()

from users.models import User, NILS_Profile
from logersn.models import Property, PricingConfig
from solvable.models import RentalFiliation, IncidentReport

def seed_master_data():
    print("🚀 Démarrage du transfert des meilleures données (Master Seed)...")
    password = "pass1234"

    # 1. Configuration des Tarifs (Péage DigitalH)
    pricing, created = PricingConfig.objects.get_or_create(id=1)
    pricing.publication_fee_rent = 1000  # 1000F par annonce location
    pricing.publication_fee_sale = 5000  # 5000F par annonce vente
    pricing.publication_fee_furnished = 2000
    pricing.boost_daily_fee = 500
    pricing.popup_daily_fee = 1000
    pricing.save()
    print("✅ Tarifs configurés avec succès.")

    # 2. Création des Profils Professionnels de Référence
    pros = [
        {
            'phone': '764443313', 'first': 'Loger', 'last': 'Sénégal', 
            'role': 'AGENCY', 'company': 'Loger Sénégal ™', 'area': 'Dakar & Régions',
            'is_staff': True, 'is_superuser': True
        },
        {
            'phone': '770000001', 'first': 'Samba', 'last': 'Immo', 
            'role': 'BROKER', 'company': 'Samba Courtage Prestige', 'area': 'Almadies, Ngor'
        },
        {
            'phone': '770000002', 'first': 'Awa', 'last': 'Bailleur', 
            'role': 'LANDLORD', 'company': 'Gestion Immobilière Awa', 'area': 'Plateau'
        }
    ]

    for p in pros:
        user, created = User.objects.get_or_create(
            phone_number=p['phone'],
            defaults={
                'first_name': p['first'],
                'last_name': p['last'],
                'role': p['role'],
                'company_name': p.get('company', ''),
                'coverage_area': p.get('area', ''),
                'is_verified_pro': True,
                'is_phone_verified': True,
                'is_staff': p.get('is_staff', False),
                'is_superuser': p.get('is_superuser', False)
            }
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"✅ Compte créé : {p['first']} {p['last']} ({p['role']})")
        
        # Profil NILS
        NILS_Profile.objects.get_or_create(
            user=user,
            defaults={'nils_type': p['role'], 'score': 100, 'reputation_status': 'GREEN'}
        )

    # 3. Génération de quelques Annonces "Vitrines"
    property_data = [
        {
            'title': 'Somptueux Penthouse avec vue sur mer',
            'type': 'APARTMENT', 'cat': 'RENT', 'price': 1500000,
            'city': 'DAKAR', 'neighborhood': 'ALMADIES', 'rooms': 5
        },
        {
            'title': 'Villa d\'architecte avec piscine',
            'type': 'VILLA', 'cat': 'SALE', 'price': 450000000,
            'city': 'DAKAR', 'neighborhood': 'NGOR', 'rooms': 8
        }
    ]

    landlord = User.objects.get(phone_number='764443313')
    for pd in property_data:
        prop, created = Property.objects.get_or_create(
            title=pd['title'],
            owner=landlord,
            defaults={
                'property_type': pd['type'],
                'listing_category': pd['cat'],
                'price': pd['price'],
                'city': pd['city'],
                'neighborhood': pd['neighborhood'],
                'total_rooms': pd['rooms'],
                'is_published': True,
                'is_paid': True,
                'is_boosted': True
            }
        )
        if created:
            print(f"✅ Annonce créée : {pd['title']}")

    print("\n🏁 Transfert des meilleures données terminé !")
    print(f"🔑 Accès Admin principal : {pros[0]['phone']} / {password}")

if __name__ == "__main__":
    seed_master_data()
