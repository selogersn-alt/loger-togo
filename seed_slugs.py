import os
import django
import sys

# Configuration de Django
sys.path.append('/home/gaak4328/logersenegal.com')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')
django.setup()

from users.models import User
from django.utils.text import slugify

def generate_slugs():
    print("Début de la génération des slugs...")
    # On cible uniquement les pros qui n'ont pas encore de slug
    users_without_slug = User.objects.filter(slug__isnull=True) | User.objects.filter(slug='')
    
    count = 0
    for user in users_without_slug:
        # On utilise le nom de l'agence ou le nom/prénom
        base_name = user.company_name or f"{user.first_name}-{user.last_name}"
        if not base_name or base_name == "None-None":
            base_name = str(user.phone_number)
        
        new_slug = slugify(base_name)
        
        # Unicité
        unique_slug = new_slug
        num = 1
        while User.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{new_slug}-{num}"
            num += 1
            
        user.slug = unique_slug
        user.save()
        count += 1
        print(f"Slug généré pour {user.phone_number}: {unique_slug}")

    print(f"Terminé ! {count} slugs ont été générés.")

if __name__ == "__main__":
    generate_slugs()
