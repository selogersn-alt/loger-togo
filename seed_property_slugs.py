import os
import django
import sys

# Configuration de Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')
django.setup()

from logersn.models import Property

def generate_property_slugs():
    print("Analyses des annonces pour la génération des slugs...")
    # On récupère les annonces qui n'ont pas encore de slug
    props = Property.objects.filter(slug__isnull=True) | Property.objects.filter(slug='')
    
    count = 0
    for p in props:
        # La méthode save() que j'ai modifiée tout à l'heure va s'occuper du reste
        p.save()
        count += 1
        print(f"Slug généré pour l'annonce '{p.title}' (ID: {str(p.id)[:8]}) -> {p.slug}")
        
    print(f"\nSuccès ! {count} annonces ont été mises à jour avec des URLs SEO.")

if __name__ == "__main__":
    generate_property_slugs()
