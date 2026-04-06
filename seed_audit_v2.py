import os
import django
import uuid
from decimal import Decimal
from django.utils import timezone
import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')
django.setup()

from users.models import User, NILS_Profile
from solvable.models import RentalFiliation, IncidentReport, PaymentHistory
from logersn.models import Property

def seed_audit():
    print("--- Démarrage du Seeding Audit Complet ---")
    
    password = "pass1234"

    # 1. Création des Professionnels
    landlord, _ = User.objects.get_or_create(
        phone_number="770000010",
        defaults={
            "first_name": "Jean",
            "last_name": "Bailleur",
            "role": "LANDLORD",
            "is_verified_pro": True,
            "is_phone_verified": True
        }
    )
    landlord.set_password(password)
    landlord.save()

    broker, _ = User.objects.get_or_create(
        phone_number="770000020",
        defaults={
            "first_name": "Samba",
            "last_name": "Courtier",
            "role": "BROKER",
            "is_verified_pro": True,
            "is_phone_verified": True,
            "company_name": "Samba Immo"
        }
    )
    broker.set_password(password)
    broker.save()

    # Propriété pour les tests
    prop, _ = Property.objects.get_or_create(
        title="Villa de Test Audit",
        defaults={
            "owner": landlord,
            "property_type": "VILLA",
            "city": "DAKAR",
            "neighborhood": "ALMADIES",
            "rent_price": 500000,
        }
    )

    # 2. Création des Scénarios de Signalements
    
    scenarios = [
        {
            "phone": "775000001",
            "first": "Adama", "last": "Loyer",
            "incident_type": "UNPAID_RENT",
            "status": "IMPACTED",
            "desc": "3 mois de loyers impayés (1.500.000 FCFA). Procédure d'expulsion en cours.",
            "reporter": landlord
        },
        {
            "phone": "775000002",
            "first": "Bineta", "last": "Commission",
            "incident_type": "UNPAID_COMMISSION",
            "status": "IMPACTED",
            "desc": "N'a jamais payé les frais de courtage après avoir emménagé.",
            "reporter": broker
        },
        {
            "phone": "775000003",
            "first": "Cheikh", "last": "Retard",
            "incident_type": "LATE_PAYMENT",
            "status": "IN_MEDIATION",
            "desc": "Paye systématiquement avec 15 jours de retard depuis 6 mois.",
            "reporter": landlord
        },
        {
            "phone": "775000004",
            "first": "Doudou", "last": "Degats",
            "incident_type": "PROPERTY_DAMAGE",
            "status": "IMPACTED",
            "desc": "A cassé les sanitaires et les vitres lors de son départ sans réparer.",
            "reporter": landlord
        },
        {
            "phone": "775000005",
            "first": "Esther", "last": "Conflit",
            "incident_type": "BAD_BEHAVIOR",
            "status": "IN_MEDIATION",
            "desc": "Nuisances sonores répétées et altercations physiques avec le voisinage.",
            "reporter": landlord
        },
        {
            "phone": "775000006",
            "first": "Fatou", "last": "Autre",
            "incident_type": "OTHER",
            "status": "RESOLVED",
            "desc": "Sous-location non autorisée (Résolu après mise en demeure).",
            "reporter": landlord
        },
        {
            "phone": "775000007",
            "first": "Gaby", "last": "Zen",
            "incident_type": None, # Locataire parfait
            "status": None,
            "desc": None,
            "reporter": None
        }
    ]

    for sc in scenarios:
        user, _ = User.objects.get_or_create(
            phone_number=sc["phone"],
            defaults={
                "first_name": sc["first"],
                "last_name": sc["last"],
                "role": "TENANT",
                "is_phone_verified": True
            }
        )
        user.set_password(password)
        user.save()
        
        profile, _ = NILS_Profile.objects.get_or_create(user=user)
        
        if sc["incident_type"]:
            # Création d'une filiation
            filiation, _ = RentalFiliation.objects.get_or_create(
                landlord=landlord,
                tenant=user,
                property=prop,
                defaults={"monthly_rent": 500000, "start_date": timezone.now().date() - datetime.timedelta(days=100)}
            )
            filiation.status = 'ACTIVE'
            filiation.save()
            
            # Création du signalement
            IncidentReport.objects.get_or_create(
                rental_filiation=filiation,
                reported_tenant=user,
                reporter=sc["reporter"],
                incident_type=sc["incident_type"],
                defaults={
                    "amount_due": 100000 if sc["incident_type"] in ['UNPAID_RENT', 'PROPERTY_DAMAGE', 'UNPAID_COMMISSION'] else 0,
                    "description": sc["desc"],
                    "status": sc["status"]
                }
            )
        
        # Recalcul du score NILS
        profile.update_score()
        print(f"Créé: {user.first_name} {user.last_name} ({user.phone_number}) - Score: {profile.score} ({profile.reputation_status})")

    print("\n--- Seeding terminé ---")
    print(f"Accès commun: Mot de passe = '{password}'")

if __name__ == "__main__":
    seed_audit()
