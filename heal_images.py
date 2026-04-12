import os
import django
import sys

# Ajouter le répertoire courant au path pour l'import des réglages
sys.path.append(os.getcwd())

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logersenegal.settings')
django.setup()

from logersn.models import PropertyImage
from django.conf import settings

def heal_images():
    print("--- Démarrage de la guérison des images ---")
    # On cherche les images qui contiennent .webp (la corruption)
    corrupted_images = PropertyImage.objects.filter(image_url__icontains='.webp')
    fixed_count = 0
    not_found_count = 0

    extensions_to_check = ['.jpg', '.jpeg', '.png', '.JPG', '.PNG', '.JPEG']

    for img in corrupted_images:
        current_name = img.image_url.name
        # On récupère le nom sans l'extension .webp
        base_name = os.path.splitext(current_name)[0]
        
        found = False
        for ext in extensions_to_check:
            test_path = f"{base_name}{ext}"
            full_path = os.path.join(settings.MEDIA_ROOT, test_path)
            
            if os.path.exists(full_path):
                print(f"Fix trouvé pour {img.id} : {current_name} -> {test_path}")
                img.image_url.name = test_path
                img.save()
                fixed_count += 1
                found = True
                break
        
        if not found:
            print(f"Attention : Aucun fichier physique trouvé pour {current_name} (Base: {base_name})")
            not_found_count += 1

    print(f"\n--- Résumé ---")
    print(f"Images réparées : {fixed_count}")
    print(f"Images restées en erreur : {not_found_count}")

if __name__ == "__main__":
    heal_images()
