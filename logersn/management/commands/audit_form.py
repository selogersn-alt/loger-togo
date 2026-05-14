from django.core.management.base import BaseCommand
from logersn.models import Property
from logersn.forms import PropertyForm

class Command(BaseCommand):
    help = 'Audit du backend Loger Togo (Modèles et Formulaires)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🔍 Audit du backend Loger Togo..."))
        
        # 1. Vérification des champs critiques dans le modèle
        model_fields = [f.name for f in Property._meta.get_fields()]
        required_fields = ['price', 'price_per_night', 'listing_category', 'document_type']
        
        for field in required_fields:
            if field in model_fields:
                self.stdout.write(f"✅ Champ '{field}' présent dans le modèle Property.")
            else:
                self.stdout.write(self.style.ERROR(f"❌ Champ '{field}' MANQUANT dans le modèle Property !"))

        # 2. Vérification du formulaire
        form = PropertyForm()
        form_fields = form.fields.keys()
        
        self.stdout.write("\n📝 Audit du PropertyForm...")
        if 'price_per_night' in form_fields:
            self.stdout.write(self.style.SUCCESS("✅ 'price_per_night' est bien dans le formulaire."))
        else:
            self.stdout.write(self.style.ERROR("❌ 'price_per_night' MANQUANT dans le formulaire."))
        
        if 'document_type' in form_fields:
            self.stdout.write(self.style.SUCCESS("✅ 'document_type' est bien dans le formulaire."))
        else:
            self.stdout.write(self.style.ERROR("❌ 'document_type' MANQUANT dans le formulaire."))

        self.stdout.write(self.style.SUCCESS("\n✨ Audit terminé avec succès."))
