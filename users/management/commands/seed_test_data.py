from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import KYCProfile
from logersn.models import Property, PropertyImage
import random
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds fictional data for testing purposes'

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        # 1. Create 4 Agents
        agent_data = [
            ("901000001", "agent1@logertg.com", "Lomé Plateau", "Agent Kodjo Immobilier"),
            ("901000002", "agent2@logertg.com", "Agoè-Assiyéyé", "Koffi Agence"),
            ("901000003", "agent3@logertg.com", "Adidogomé", "Alovor Immo"),
            ("901000004", "agent4@logertg.com", "Baguida", "Elite Agent Togo"),
        ]
        agents = []
        for phone, email, area, company in agent_data:
            user, created = User.objects.get_or_create(
                phone_number=phone,
                defaults={
                    'email': email,
                    'coverage_area': area,
                    'company_name': company,
                    'role': User.RoleEnum.AGENT,
                    'is_verified_pro': True
                }
            )
            if created:
                user.set_password("Solvable123!")
                user.save()
            agents.append(user)

        # 2. Create 4 Landlords (Bailleurs)
        landlord_data = [
            ("991000001", "bailleur1@logertg.com", "Kara", "SCI Kabyè"),
            ("991000002", "bailleur2@logertg.com", "Lomé Centre", "M. Lawson Immobilier"),
            ("991000003", "bailleur3@logertg.com", "Aného", "Résidence du Littoral"),
            ("991000004", "bailleur4@logertg.com", "Kpalimé", "Villas de la Montagne"),
        ]
        landlords = []
        for phone, email, area, company in landlord_data:
            user, created = User.objects.get_or_create(
                phone_number=phone,
                defaults={
                    'email': email,
                    'coverage_area': area,
                    'company_name': company,
                    'role': User.RoleEnum.LANDLORD,
                    'is_verified_pro': True
                }
            )
            if created:
                user.set_password("Solvable123!")
                user.save()
            landlords.append(user)

        # 3. Create 4 Agencies
        agency_data = [
            ("901000005", "agence1@logertg.com", "Lomé / Banlieue", "Togo Gui Immo"),
            ("901000006", "agence2@logertg.com", "Sokodé", "Centrale Immobilier"),
            ("901000007", "agence3@logertg.com", "Lomé Port", "Loger Sans Stress TG"),
            ("901000008", "agence4@logertg.com", "Dapaong", "Savanes Agence"),
        ]
        agencies = []
        for phone, email, area, company in agency_data:
            user, created = User.objects.get_or_create(
                phone_number=phone,
                defaults={
                    'email': email,
                    'coverage_area': area,
                    'company_name': company,
                    'role': User.RoleEnum.AGENCY,
                    'is_verified_pro': True
                }
            )
            if created:
                user.set_password("Solvable123!")
                user.save()
            agencies.append(user)

        # 4. Create 15 Properties (including 3 Boosted)
        prop_titles = [
            "💎 Penthouse de Prestige - Vue Panoramique Lomé",
            "✨ Villa Royale avec Piscine à Baguida",
            "🌟 Résidence Meublée Grand Standing - Agoè",
            "Appartement F4 Moderne à Agoè",
            "Studio Meublé à Deckon",
            "Villa de Standing à Baguida",
            "Bureau 200m2 au Plateau",
            "Chambre Étudiant Proche Université de Lomé",
            "Appartement F3 Vue Mer à Aného",
            "Duplex de Luxe à Hedzranawoé",
            "Hangar Industriel Zone Franche Lomé",
            "Terrain Constructible 500m2 à Tsévié",
            "Local Commercial RDC Avenue de la Libération",
            "Maison de ville élégante - Nyékonakpoé",
            "Terrain Titré - Davié"
        ]
        
        all_pros = agents + landlords + agencies
        cities = ['LOME', 'KARA', 'SOKODE', 'ANEHO', 'KPALIME', 'TSEVIE', 'DAPAONG']
        p_types = ['DUPLEX', 'VILLA', 'APARTMENT_F4', 'APARTMENT_F4', 'STUDIO', 'VILLA', 'BUREAU', 'CHAMBRE_SDB', 'APARTMENT_F3', 'DUPLEX', 'COMMERCIAL', 'TERRAIN', 'COMMERCIAL', 'VILLA', 'TERRAIN']
        neighborhoods = ['Cité OUA', 'Baguida Mer', 'Agoè-2000', 'Agoè-Assiyéyé', 'Deckon', 'Baguida', 'Hanoukopé', 'Amoutiévé', 'Aného', 'Hedzranawoé', 'Akodésséwa', 'Tsévié', 'Centre-Ville', 'Nyékonakpoé', 'Davié']

        from django.utils import timezone
        import datetime

        for i in range(len(prop_titles)):
            owner = random.choice(all_pros)
            is_boosted = (i < 3)  # Les 3 premiers sont boostés
            
            prop, created = Property.objects.get_or_create(
                title=prop_titles[i],
                defaults={
                    'owner': owner,
                    'property_type': p_types[i],
                    'city': cities[i % len(cities)],
                    'neighborhood': neighborhoods[i],
                    'price': random.randint(3000000, 10000000) if is_boosted else random.randint(150000, 2000000),
                    'surface': random.randint(200, 800) if is_boosted else random.randint(50, 450),
                    'bedrooms': random.randint(3, 7) if is_boosted else random.randint(1, 5),
                    'toilets': random.randint(3, 6) if is_boosted else random.randint(1, 4),
                    'total_rooms': random.randint(5, 12) if is_boosted else random.randint(2, 8),
                    'has_garage': True if is_boosted else random.choice([True, False]),
                    'description': "PREMIUM : " + prop_titles[i] + ". " if is_boosted else "",
                    'is_published': True,
                    'is_boosted': is_boosted,
                    'boost_until': timezone.now() + datetime.timedelta(days=30) if is_boosted else None
                }
            )
            if created:
                prop.description += "Ceci est une annonce générée pour tester l'interface visuelle. Bien d'exception situé dans l'un des meilleurs quartiers, offrant confort et sécurité absolue."
                prop.save()

        self.stdout.write(self.style.SUCCESS(f"Fictional data ({len(prop_titles)} properties) seeded successfully!"))
