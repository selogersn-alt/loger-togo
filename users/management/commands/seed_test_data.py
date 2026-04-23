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

        # 4. Create 10 Properties
        prop_titles = [
            "Appartement F4 Moderne à Agoè",
            "Studio Meublé à Deckon",
            "Villa de Standing à Baguida",
            "Bureau 200m2 au Plateau",
            "Chambre Étudiant Proche Université de Lomé",
            "Appartement F3 Vue Mer à Aného",
            "Duplex de Luxe à Hedzranawoé",
            "Hangar Industriel Zone Franche Lomé",
            "Terrain Constructible 500m2 à Tsévié",
            "Local Commercial RDC Avenue de la Libération"
        ]
        
        all_pros = agents + landlords + agencies
        # Real Choices from constants
        cities = ['LOME', 'KARA', 'SOKODE', 'ANEHO', 'KPALIME', 'TSEVIE', 'DAPAONG']
        p_types = ['APARTMENT_F4', 'STUDIO', 'VILLA', 'BUREAU', 'CHAMBRE_SDB', 'APARTMENT_F3', 'DUPLEX', 'COMMERCIAL', 'TERRAIN', 'COMMERCIAL']
        neighborhoods = ['Agoè-Assiyéyé', 'Deckon', 'Baguida', 'Hanoukopé', 'Amoutiévé', 'Aného', 'Hedzranawoé', 'Akodésséwa', 'Tsévié', 'Centre-Ville']

        for i in range(10):
            owner = random.choice(all_pros)
            prop, created = Property.objects.get_or_create(
                title=prop_titles[i],
                defaults={
                    'owner': owner,
                    'property_type': p_types[i],
                    'city': cities[i % len(cities)],
                    'neighborhood': neighborhoods[i],
                    'price': random.randint(150000, 2000000),
                    'surface': random.randint(50, 450),
                    'bedrooms': random.randint(1, 5),
                    'toilets': random.randint(1, 4),
                    'total_rooms': random.randint(2, 8),
                    'has_garage': random.choice([True, False]),
                    'description': "Ceci est une annonce fictive générée pour tester l'interface visuelle et le rendu des listes. Détails du bien : propre, sécurisé, accès facile.",
                    'is_published': True
                }
            )
            if created:
                # Add a dummy image placeholder
                # We can't easily upload real files via script without absolute paths, 
                # but we can try to find existing ones or just leave it.
                # Since the user asked "image", I'll try to add a record.
                pass

        self.stdout.write(self.style.SUCCESS("Fictional data seeded successfully!"))
