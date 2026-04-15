import uuid
import io
import os
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings

User = settings.AUTH_USER_MODEL

from .constants import PROPERTY_TYPE_CHOICES, CITY_CHOICES, NEIGHBORHOOD_CHOICES

class Property(models.Model):
    class CategoryEnum(models.TextChoices):
        RENT = 'RENT', 'A louer'
        SALE = 'SALE', 'A vendre'
        FURNISHED = 'FURNISHED', 'Meublé'

    class DocumentTypeEnum(models.TextChoices):
        BAIL = 'BAIL', 'BAIL'
        TITRE_FONCIER_INDIVIDUEL = 'TITRE_FONCIER_INDIVIDUEL', 'TITRE FONCIER INDIVIDUEL'
        TITRE_FONCIER_GLOBAL = 'TITRE_FONCIER_GLOBAL', 'TITRE FONCIER GLOBAL'
        ACTE_DE_VENTE = 'ACTE_DE_VENTE', 'ACTE DE VENTE'
        DELIBERATION = 'DELIBERATION', 'DELIBERATION'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, null=True, blank=True)
    description = models.TextField()
    listing_category = models.CharField(max_length=20, choices=CategoryEnum.choices, default=CategoryEnum.RENT)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    city = models.CharField(max_length=100, choices=CITY_CHOICES, default='DAKAR')
    neighborhood = models.CharField(max_length=100, choices=NEIGHBORHOOD_CHOICES)
    document_type = models.CharField(max_length=50, choices=DocumentTypeEnum.choices, null=True, blank=True, verbose_name="Type de document")
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Prix (CFA)")
    
    # Pour les meublés uniquement
    price_per_night = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Prix par nuitée (Meublé)")
    surface = models.IntegerField(default=0, blank=True, verbose_name="Surface (m2)")
    bedrooms = models.IntegerField(default=0, blank=True, verbose_name="Nombre de chambres")
    toilets = models.IntegerField(default=0, blank=True, verbose_name="Nombre de toilettes")
    total_rooms = models.IntegerField(default=1, blank=True, verbose_name="Nombre total de pièces")
    has_garage = models.BooleanField(default=False, blank=True, verbose_name="Garage disponible")
    # Nouvelles pièces
    salons = models.IntegerField(default=0, blank=True, verbose_name="Nombre de salons")
    kitchens = models.IntegerField(default=0, blank=True, verbose_name="Nombre de cuisines")
    
    # Nouveaux extérieurs
    has_balcony = models.BooleanField(default=False, blank=True, verbose_name="Balcon")
    has_terrace = models.BooleanField(default=False, blank=True, verbose_name="Terrasse")
    has_courtyard = models.BooleanField(default=False, blank=True, verbose_name="Cour")
    has_garden = models.BooleanField(default=False, blank=True, verbose_name="Jardin")
    
    is_published = models.BooleanField(default=False)
    
    # Équipements et caractéristiques (Amenities)
    wifi = models.BooleanField(default=False, verbose_name="WiFi")
    swimming_pool = models.BooleanField(default=False, verbose_name="Piscine")
    gym = models.BooleanField(default=False, verbose_name="Salle de sport")
    air_conditioning = models.BooleanField(default=False, verbose_name="Climatisation")
    refrigerator = models.BooleanField(default=False, verbose_name="Réfrigérateur")
    washing_machine = models.BooleanField(default=False, verbose_name="Machine à laver")
    microwave = models.BooleanField(default=False, verbose_name="Micro-ondes")
    tv_cable = models.BooleanField(default=False, verbose_name="TV par câble")
    generator = models.BooleanField(default=False, verbose_name="Groupe électrogène")
    water_tank = models.BooleanField(default=False, verbose_name="Réservoir d'eau")
    
    # Géolocalisation (Optionnel)
    latitude = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)
    longitude = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)

    # Statistiques et Performance
    views_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de vues")
    clicks_count = models.PositiveIntegerField(default=0, verbose_name="Nombre de clics d'action")

    # Options de Monétisation DigitalH
    is_boosted = models.BooleanField(default=False, verbose_name="Annonce Boostée")
    boost_until = models.DateTimeField(null=True, blank=True, verbose_name="Boost valide jusqu'au")
    
    is_featured_popup = models.BooleanField(default=False, verbose_name="Mise en avant Pop-up")
    popup_until = models.DateTimeField(null=True, blank=True, verbose_name="Pop-up valide jusqu'au")

    is_paid = models.BooleanField(default=False, verbose_name="Frais de publication payés")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.slug:
            return reverse('property_detail_slug', kwargs={'slug': self.slug})
        return reverse('property_detail', kwargs={'property_id': self.id})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = "propriete"
            # On ajoute une partie de l'ID pour garantir l'unicité absolue
            self.slug = f"{base_slug}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)

    def get_main_image(self):
        primary_image = self.images.filter(is_primary=True).first()
        if primary_image:
            return primary_image
        return self.images.first()
        
    def get_icon_class(self):
        t = self.property_type
        if 'APARTMENT' in t:
            return 'fa-building'
        elif t in ['STUDIO', 'MINI_STUDIO', 'STUDIO_ENTREE_SALON', 'STUDIO_SEPARE', 'CHAMBRE_SDB_INTERNE', 'CHAMBRE_SIMPLE', 'COLOCATION', 'STUDIO_AMERICAIN', 'MINI_STUDIO_AMERICAIN']:
            return 'fa-door-open'
        elif t == 'IMMEUBLE':
            return 'fa-city'
        elif t in ['VILLA', 'MAISON', 'DUPLEX', 'TRIPLEX']:
            return 'fa-house-chimney'
        elif t == 'TERRAIN':
            return 'fa-map-location-dot'
        elif t in ['COMMERCIAL', 'BOUTIQUE', 'MAGASIN', 'SHOWROOM']:
            return 'fa-store'
        elif t in ['BUREAU', 'USAGE_PRO']:
            return 'fa-briefcase'
        return 'fa-house'

class PropertyImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image_url = models.FileField(upload_to='properties/')
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """Conversion automatique en WebP et redimensionnement intelligent (Sécurisé)."""
        if self.image_url:
            try:
                # On ne tente la conversion que si Pillow est disponible et le fichier n'est pas déjà webp
                if not self.image_url.name.lower().endswith('.webp'):
                    img = Image.open(self.image_url)
                    
                    # 1. Conversion en RGB
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    
                    # 2. Redimensionnement
                    max_width = 1200
                    if img.width > max_width:
                        output_size = (max_width, int((max_width / img.width) * img.height))
                        img = img.resize(output_size, Image.LANCZOS)
                    
                    # 3. Flux mémoire
                    output = io.BytesIO()
                    img.save(output, format='WEBP', quality=85)
                    output.seek(0)
                    
                    # 4. Changement de nom et sauvegarde du champ
                    current_name = os.path.splitext(self.image_url.name)[0]
                    new_filename = f"{current_name}.webp"
                    self.image_url.save(new_filename, ContentFile(output.read()), save=False)
            except Exception as e:
                # En cas d'erreur (PIL manquant, erreur de format, etc.), on ignore et on garde l'original
                print(f"WebP conversion failed for {self.image_url.name}: {e}")
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.property.title}"

class Transaction(models.Model):
    class TypeEnum(models.TextChoices):
        PUBLICATION = 'PUBLICATION', 'Frais de Publication'
        BOOST = 'BOOST', 'Boost d\'Annonce'
        POPUP = 'POPUP', 'Mise en avant Pop-up'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TypeEnum.choices)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True, verbose_name="Référence FedaPay / Interne")
    status = models.CharField(max_length=20, choices=[('PENDING', 'En attente'), ('SUCCESS', 'Réussite'), ('FAILED', 'Échec')], default='PENDING')
    days = models.IntegerField(default=1, verbose_name="Nombre de jours")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions (Comptabilité)"

    def __str__(self):
        return f"{self.user} - {self.transaction_type} - {self.amount}F"

class PricingConfig(models.Model):
    publication_fee_rent = models.DecimalField(max_digits=20, decimal_places=2, default=100.00, verbose_name="Prix Publication (Location)")
    publication_fee_sale = models.DecimalField(max_digits=20, decimal_places=2, default=500.00, verbose_name="Prix Publication (Vente)")
    publication_fee_furnished = models.DecimalField(max_digits=20, decimal_places=2, default=300.00, verbose_name="Prix Publication (Meublé)")
    
    boost_daily_fee = models.DecimalField(max_digits=20, decimal_places=2, default=100.00, verbose_name="Prix Boost par jour")
    popup_daily_fee = models.DecimalField(max_digits=20, decimal_places=2, default=500.00, verbose_name="Prix Pop-up par jour")

    class Meta:
        verbose_name = "Paramètres des Tarifs"
        verbose_name_plural = "Paramètres des Tarifs (DigitalH)"

    def __str__(self):
        return "Configuration des tarifs DigitalH"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user} favorited {self.property}"

class PropertyEquipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='interior_equipments')
    name = models.CharField(max_length=100, help_text="Ex: Réfrigérateur, Climatiseur, TV...")
    brand = models.CharField(max_length=100, blank=True, null=True, help_text="Marque optionnelle")
    icon_class = models.CharField(max_length=50, default='fa-plug', help_text="Icône FontAwesome (ex: fa-tv, fa-snowflake)")
    
    def __str__(self):
        return f"{self.name} for {self.property.title}"
