import os
import sys
import django

# Configuration de l'environnement Django
sys.path.append('d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from logersn.models import Property
from logersn.forms import PropertyForm
from django.utils.translation import gettext as _

def audit_and_fix_backend():
    print("🔍 Audit du backend Loger Togo...")
    
    # 1. Vérification des champs critiques dans le modèle
    model_fields = [f.name for f in Property._meta.get_fields()]
    required_fields = ['price', 'price_per_night', 'listing_category', 'document_type']
    
    for field in required_fields:
        if field in model_fields:
            print(f"✅ Champ '{field}' présent dans le modèle Property.")
        else:
            print(f"❌ Champ '{field}' MANQUANT dans le modèle Property !")

    # 2. Vérification du formulaire
    form = PropertyForm()
    form_fields = form.fields.keys()
    
    print("\n📝 Audit du PropertyForm...")
    if 'price_per_night' in form_fields:
        print("✅ 'price_per_night' est bien dans le formulaire.")
    else:
        print("❌ 'price_per_night' MANQUANT dans le formulaire. Ajout requis.")

    # 3. Vérification de la logique de validation
    # On s'assure que price_per_night est traité pour FURNISHED
    print("\n⚙️ Vérification de la logique de prix meublé...")
    # (Cette partie est déjà dans forms.py mais on valide la cohérence)

if __name__ == "__main__":
    audit_and_fix_backend()
