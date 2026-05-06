import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from logersn.models import Property, PropertyAlert
from logersn.utils import trigger_property_alerts
from django.contrib.auth import get_user_model

def run_test():
    User = get_user_model()
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        admin = User.objects.create_superuser('admin_test', 'admin@test.com', 'pass')

    # 1. Créer une alerte de test
    PropertyAlert.objects.all().delete()
    alert = PropertyAlert.objects.create(
        email='mursd@test.com',
        city='LOME',
        property_type='VILLA',
        max_price=1000000
    )
    print(f"Alerte créée pour : {alert.email}")

    # 2. Créer une propriété qui match
    prop = Property.objects.create(
        owner=admin,
        title="Villa Royale Test Matching",
        city='LOME',
        property_type='VILLA',
        listing_category='RENT',
        price=750000,
        neighborhood='Cité OUA'
    )
    print(f"Propriété créée : {prop.title} à {prop.price} FCFA")

    # 3. Déclencher le matching
    count = trigger_property_alerts(prop)
    print(f"Résultat du matching : {count} e-mail(s) envoyé(s)")

    if count > 0:
        print("✅ SUCCÈS : Le système de matching fonctionne !")
    else:
        print("❌ ÉCHEC : Aucune alerte envoyée.")

if __name__ == "__main__":
    run_test()
