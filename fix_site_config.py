import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')
django.setup()

from django.contrib.sites.models import Site

def fix_site():
    try:
        # On récupère le site avec l'ID configuré dans settings.py (SITE_ID = 1)
        site = Site.objects.get(id=1)
        # On force le domaine PROPRE (sans https://)
        site.domain = 'logersenegal.com'
        site.name = 'Loger Sénégal'
        site.save()
        print(f"✅ Succès : Site mis à jour - {site.domain} ({site.name})")
    except Site.DoesNotExist:
        # Si le site 1 n'existe pas, on le crée
        site = Site.objects.create(id=1, domain='logersenegal.com', name='Loger Sénégal')
        print(f"✅ Succès : Site créé - {site.domain} ({site.name})")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    fix_site()
