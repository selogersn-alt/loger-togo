import uuid
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from logersn.models import Property, PropertyImage, Transaction
from logersn.constants import PROPERTY_TYPE_CHOICES, CITY_CHOICES

class Command(BaseCommand):
    help = 'Remplit la base de données avec des données de test pour Loger Togo'

    def handle(self, *args, **kwargs):
        self.stdout.write("Début du remplissage des données...")

        # 1. Création des utilisateurs
        landlord, _ = User.objects.get_or_create(
            phone_number="+22890000001",
            defaults={
                'first_name': 'Jean',
                'last_name': 'Bailleur',
                'role': 'LANDLORD',
                'is_phone_verified': True,
                'email': 'jean@example.com'
            }
        )
        landlord.set_password('password123')
        landlord.save()

        tenant, _ = User.objects.get_or_create(
            phone_number="+22890000002",
            defaults={
                'first_name': 'Marie',
                'last_name': 'Locataire',
                'role': 'TENANT',
                'is_phone_verified': True,
                'email': 'marie@example.com'
            }
        )
        tenant.set_password('password123')
        tenant.save()

        agency, _ = User.objects.get_or_create(
            phone_number="+22890000003",
            defaults={
                'company_name': 'Togo Immo Agence',
                'role': 'AGENCY',
                'is_verified_pro': True,
                'is_phone_verified': True,
                'email': 'contact@togoimmo.tg'
            }
        )
        agency.set_password('password123')
        agency.save()

        self.stdout.write(self.style.SUCCESS("Utilisateurs créés !"))

        # 2. Création des Propriétés
        properties_data = [
            {
                'title': 'Appartement F3 Moderne à Adidogomé',
                'description': 'Bel appartement avec 2 chambres, salon, cuisine équipée. Zone calme et sécurisée.',
                'listing_category': 'RENT',
                'property_type': 'APARTMENT_F3',
                'city': 'LOME',
                'neighborhood': 'Adidogomé',
                'price': 150000,
                'owner': landlord
            },
            {
                'title': 'Villa de Luxe avec Piscine à Baguida',
                'description': 'Magnifique villa 5 pièces, piscine, grand jardin, garage pour 3 voitures.',
                'listing_category': 'SALE',
                'property_type': 'VILLA',
                'city': 'LOME',
                'neighborhood': 'Baguida',
                'price': 85000000,
                'owner': agency
            },
            {
                'title': 'Studio Meublé Tout Confort - Deckon',
                'description': 'Studio idéal pour vos séjours courts. WiFi, clim, Canal+ inclus.',
                'listing_category': 'FURNISHED',
                'property_type': 'STUDIO_AMERICAIN',
                'city': 'LOME',
                'neighborhood': 'Deckon',
                'price': 25000,
                'price_per_night': 25000,
                'owner': landlord
            },
            {
                'title': 'Terrain 1/2 lot à Agoè-Assiyéyé',
                'description': 'Terrain plat, déjà clôturé, proche de la route goudronnée.',
                'listing_category': 'SALE',
                'property_type': 'TERRAIN',
                'city': 'LOME',
                'neighborhood': 'Agoè',
                'price': 12000000,
                'owner': agency
            }
        ]

        for p_data in properties_data:
            prop, created = Property.objects.get_or_create(
                title=p_data['title'],
                defaults={
                    'description': p_data['description'],
                    'listing_category': p_data['listing_category'],
                    'property_type': p_data['property_type'],
                    'city': p_data['city'],
                    'neighborhood': p_data['neighborhood'],
                    'price': p_data['price'],
                    'price_per_night': p_data.get('price_per_night'),
                    'owner': p_data['owner'],
                    'is_published': True
                }
            )
            if created:
                # Ajouter une transaction factice pour simuler le paiement de publication
                Transaction.objects.create(
                    user=p_data['owner'],
                    property=prop,
                    transaction_type='PUBLICATION',
                    amount=0,
                    reference=f"SEED-{uuid.uuid4().hex[:8]}",
                    status='SUCCESS'
                )

        self.stdout.write(self.style.SUCCESS("Propriétés et transactions créées !"))
        self.stdout.write(self.style.SUCCESS("Tout est prêt pour les tests locaux."))
