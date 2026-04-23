import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Logertogo.settings')
django.setup()

from users.models import User
from django.core.management import call_command

from django.contrib.sites.models import Site

# 1. Configuration du Domaine pour le Sitemap
domain = 'solvable.logertg.com'
site, created = Site.objects.get_or_create(id=1)
site.domain = domain
site.name = 'Solvable SN'
site.save()
print(f"Site configuré sur le domaine : {domain}")

# 2. Création de votre Super-Administrateur (si n'existe pas)
# Remplacez '+228770000000' et 'admin123' par ce que vous voulez ci-dessous
ADMIN_PHONE = os.getenv('ADMIN_PHONE', '+228764443313')
ADMIN_PASS = os.getenv('ADMIN_PASS', 'admin123')

if not User.objects.filter(phone_number=ADMIN_PHONE).exists():
    print(f"Création du super-utilisateur {ADMIN_PHONE}...")
    User.objects.create_superuser(phone_number=ADMIN_PHONE, password=ADMIN_PASS, role='SUB_ADMIN')
    print("Super-utilisateur créé avec succès.")
else:
    # Si l'utilisateur existe déjà, on met à jour son mot de passe pour qu'il corresponde à la variable Render
    u = User.objects.get(phone_number=ADMIN_PHONE)
    u.set_password(ADMIN_PASS)
    u.is_staff = True
    u.is_superuser = True
    u.save()
    print(f"Accès administrateur mis à jour pour {ADMIN_PHONE}.")

# 3. Configuration des Tarifs DigitalH (si n'existe pas)
from logersn.models import PricingConfig
if not PricingConfig.objects.exists():
    print("Initialisation des tarifs par défaut...")
    PricingConfig.objects.create(
        publication_fee_rent=100.0,
        publication_fee_sale=500.0,
        publication_fee_furnished=300.0,
        boost_daily_fee=100.0,
        popup_daily_fee=500.0
    )
    print("Tarifs DigitalH initialisés avec succès.")

# 4. Lancement du script de peuplement (Seed)
print("Peuplement de la base de données avec des profils fictifs...")
try:
    # On importe le script seed si il est présent
    import seed_all_roles
    print("Données fictives injectées avec succès.")
except Exception as e:
    print(f"Erreur lors du peuplement : {e}")
