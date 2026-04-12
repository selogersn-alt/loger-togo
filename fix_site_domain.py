import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')
django.setup()

from django.contrib.sites.models import Site

def fix_site_domain():
    print("🔍 Vérification du domaine SITE_ID...")
    try:
        site = Site.objects.get(id=1)
        print(f"Domaine actuel : {site.domain}")
        
        if "https://" in site.domain or "http://" in site.domain:
            new_domain = site.domain.replace("https://", "").replace("http://", "").strip("/")
            print(f"🛠️ Correction du domaine : {site.domain} -> {new_domain}")
            site.domain = new_domain
            site.name = "Loger Sénégal"
            site.save()
            print("✅ Domaine corrigé avec succès.")
        else:
            print("✨ Le domaine semble déjà correct.")
            
    except Exception as e:
        print(f"❌ Erreur lors de la correction : {e}")

if __name__ == "__main__":
    fix_site_domain()
