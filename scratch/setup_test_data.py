import os
import django
import sys
import uuid
import random

# Setup Django
sys.path.append('d:/HDIGITAL/ANDROID_ANTIGRAVITY/LOGERTOGO')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from users.models import User
from logersn.models import Property, PropertyImage
from django.utils.text import slugify
from django.utils import timezone

from management.models import Lease, RentPayment, MaintenanceRequest
from logersn.models import Property, PropertyImage, Favorite, Transaction, PropertyReview, PropertyEquipment

def setup_data():
    print("--- NETTOYAGE ET INITIALISATION DES DONNÉES TEST TOGO ---")
    
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('PRAGMA foreign_keys = OFF;')
    
    # 1. Supprimer les données dépendantes
    RentPayment.objects.all().delete()
    MaintenanceRequest.objects.all().delete()
    Lease.objects.all().delete()
    Transaction.objects.all().delete()
    Favorite.objects.all().delete()
    PropertyReview.objects.all().delete()
    PropertyEquipment.objects.all().delete()
    PropertyImage.objects.all().delete()
    Property.objects.all().delete()
    
    cursor.execute('PRAGMA foreign_keys = ON;')
    print("Base de données nettoyée (Annonces, Baux, Transactions, Favoris).")

    # 2. Création des comptes de test
    # Admin
    admin_user, created = User.objects.get_or_create(
        phone_number="+22899110000",
        defaults={
            'first_name': 'Admin',
            'last_name': 'LogerTogo',
            'role': 'SUB_ADMIN',
            'is_staff': True,
            'is_superuser': True,
            'email': 'admin@logertogo.com'
        }
    )
    if created: admin_user.set_password('admin1234'); admin_user.save()
    print(f"Compte Admin: {admin_user.phone_number} / admin1234")

    # Agence
    agency_user, created = User.objects.get_or_create(
        phone_number="+22890123456",
        defaults={
            'first_name': 'Agence',
            'last_name': 'ImmoTogo',
            'company_name': 'ImmoTogo Properties Lomé',
            'role': 'AGENCY',
            'email': 'contact@immotogo.tg',
            'is_verified_pro': True
        }
    )
    if created: agency_user.set_password('pro1234'); agency_user.save()
    print(f"Compte Agence: {agency_user.phone_number} / pro1234")

    # Locataire
    tenant_user, created = User.objects.get_or_create(
        phone_number="+22892334455",
        defaults={
            'first_name': 'Koffi',
            'last_name': 'Locataire',
            'role': 'TENANT',
            'email': 'koffi@email.tg'
        }
    )
    if created: tenant_user.set_password('test1234'); tenant_user.save()
    print(f"Compte Locataire: {tenant_user.phone_number} / test1234")

    # 3. Création des nouvelles annonces fictives au Togo
    togo_data = [
        {
            'title': 'Superbe Villa à Baguida',
            'desc': 'Villa moderne de 4 chambres avec piscine et jardin à Baguida, Lomé.',
            'city': 'LOME', 'neighborhood': 'Baguida', 'price': 850000, 'cat': 'RENT', 'type': 'VILLA'
        },
        {
            'title': 'Appartement F3 Haut Standing - Agoé',
            'desc': 'Appartement climatisé au 2ème étage à Agoé Assiyéyé. Sécurité 24h/24.',
            'city': 'LOME', 'neighborhood': 'Agoé', 'price': 250000, 'cat': 'RENT', 'type': 'APARTMENT'
        },
        {
            'title': 'Terrain 1 lot à Adidogomé',
            'desc': 'Terrain titré de 600m2 idéal pour projet immobilier à Adidogomé Yokoe.',
            'city': 'LOME', 'neighborhood': 'Adidogomé', 'price': 15000000, 'cat': 'SALE', 'type': 'LAND'
        },
        {
            'title': 'Studio Meublé Chic à Nyékonakpoé',
            'desc': 'Studio tout équipé avec Wifi et Canal+ à Nyékonakpoé, centre-ville.',
            'city': 'LOME', 'neighborhood': 'Nyékonakpoé', 'price': 35000, 'cat': 'FURNISHED', 'type': 'STUDIO'
        },
        {
            'title': 'Maison de vacances à Kpalimé',
            'desc': 'Maison calme avec vue sur les montagnes de Kpalimé. Idéal pour repos.',
            'city': 'KPALIME', 'neighborhood': 'Kpodji', 'price': 450000, 'cat': 'RENT', 'type': 'HOUSE'
        },
        {
            'title': 'Bureau Professionnel - Quartier Administratif',
            'desc': 'Espace bureau de 80m2 proche des ministères à Lomé Amoutivé.',
            'city': 'LOME', 'neighborhood': 'Amoutivé', 'price': 500000, 'cat': 'RENT', 'type': 'OFFICE'
        },
    ]

    for data in togo_data:
        p = Property.objects.create(
            owner=agency_user,
            title=data['title'],
            description=data['desc'],
            listing_category=data['cat'],
            property_type=data['type'],
            city=data['city'],
            neighborhood=data['neighborhood'],
            price=data['price'],
            is_published=True,
            is_paid=True
        )
        print(f"Annonce créée: {p.title} à {p.neighborhood}")

    print("--- TERMINÉ ---")

if __name__ == "__main__":
    setup_data()
