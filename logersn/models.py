import uuid
import io
import os
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings

User = settings.AUTH_USER_MODEL

from .constants import PROPERTY_TYPE_CHOICES, CITY_CHOICES

class Property(models.Model):
    class CategoryEnum(models.TextChoices):
        RENT = 'RENT', _('En location')
        SALE = 'SALE', _('En vente')
        FURNISHED = 'FURNISHED', _('Meublé')

    class DocumentTypeEnum(models.TextChoices):
        BAIL = 'BAIL', _('Bail')
        TITRE_FONCIER_INDIVIDUEL = 'TITRE_FONCIER_INDIVIDUEL', _('Titre Foncier Individuel')
        TITRE_FONCIER_GLOBAL = 'TITRE_FONCIER_GLOBAL', _('Titre Foncier Global')
        ACTE_DE_VENTE = 'ACTE_DE_VENTE', _('Acte de Vente')
        DELIBERATION = 'DELIBERATION', _('Délibération')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField()
    listing_category = models.CharField(max_length=20, choices=CategoryEnum.choices, default=CategoryEnum.RENT, db_index=True)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES, db_index=True)
    city = models.CharField(max_length=100, choices=CITY_CHOICES, default='LOME', db_index=True)
    neighborhood = models.CharField(max_length=100, verbose_name=_("Quartier"))
    document_type = models.CharField(max_length=50, choices=DocumentTypeEnum.choices, null=True, blank=True, verbose_name=_("Type de document"))
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=_("Prix (CFA)"))
    
    # Pour les meublés uniquement
    price_per_night = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name=_("Prix par nuitée (Meublé)"))
    surface = models.IntegerField(default=0, blank=True, verbose_name=_("Surface (m2)"))
    bedrooms = models.IntegerField(default=0, blank=True, verbose_name=_("Nombre de chambres"))
    toilets = models.IntegerField(default=0, blank=True, verbose_name=_("Nombre de toilettes"))
    total_rooms = models.IntegerField(default=1, blank=True, verbose_name=_("Nombre total de pièces"))
    households = models.IntegerField(default=0, blank=True, verbose_name=_("Nombre de ménages"))
    floor_level = models.IntegerField(default=0, blank=True, verbose_name=_("Niveau d'étage"))
    has_garage = models.BooleanField(default=False, blank=True, verbose_name=_("Garage disponible"))
    # Nouvelles pièces
    salons = models.IntegerField(default=0, blank=True, verbose_name=_("Nombre de salons"))
    kitchens = models.IntegerField(default=0, blank=True, verbose_name=_("Nombre de cuisines"))
    
    # Nouveaux extérieurs
    has_balcony = models.BooleanField(default=False, blank=True, verbose_name=_("Balcon"))
    has_terrace = models.BooleanField(default=False, blank=True, verbose_name=_("Terrasse"))
    has_courtyard = models.BooleanField(default=False, blank=True, verbose_name=_("Cour"))
    has_garden = models.BooleanField(default=False, blank=True, verbose_name=_("Jardin"))
    
    is_published = models.BooleanField(default=False, db_index=True)
    
    # Équipements et caractéristiques (Amenities)
    wifi = models.BooleanField(default=False, verbose_name=_("WiFi"))
    swimming_pool = models.BooleanField(default=False, verbose_name=_("Piscine"))
    gym = models.BooleanField(default=False, verbose_name=_("Salle de sport"))
    air_conditioning = models.BooleanField(default=False, verbose_name=_("Climatisation"))
    refrigerator = models.BooleanField(default=False, verbose_name=_("Réfrigérateur"))
    washing_machine = models.BooleanField(default=False, verbose_name=_("Machine à laver"))
    microwave = models.BooleanField(default=False, verbose_name=_("Micro-ondes"))
    tv_cable = models.BooleanField(default=False, verbose_name=_("TV par câble"))
    generator = models.BooleanField(default=False, verbose_name=_("Groupe électrogène"))
    water_tank = models.BooleanField(default=False, verbose_name=_("Réservoir d'eau"))
    
    # Géolocalisation (Optionnel)
    latitude = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)
    longitude = models.DecimalField(max_digits=15, decimal_places=10, null=True, blank=True)

    # Statistiques et Performance
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("Nombre de vues"))
    clicks_count = models.PositiveIntegerField(default=0, verbose_name=_("Nombre de clics d'action"))

    # Options de Monétisation DigitalH
    is_boosted = models.BooleanField(default=False, verbose_name=_("Annonce Boostée"))
    boost_until = models.DateTimeField(null=True, blank=True, verbose_name=_("Boost valide jusqu'au"))
    
    is_featured_popup = models.BooleanField(default=False, verbose_name=_("Mise en avant Pop-up"))
    popup_until = models.DateTimeField(null=True, blank=True, verbose_name=_("Pop-up valide jusqu'au"))

    is_paid = models.BooleanField(default=False, verbose_name=_("Frais de publication payés"))
    
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
        if self.image_url and self._state.adding:
            try:
                if not self.image_url.name.lower().endswith('.webp'):
                    img = Image.open(self.image_url)
                    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                    
                    max_width = 1200
                    if img.width > max_width:
                        output_size = (max_width, int((max_width / img.width) * img.height))
                        img = img.resize(output_size, Image.LANCZOS)
                    
                    output = io.BytesIO()
                    img.save(output, format='WEBP', quality=80)
                    output.seek(0)
                    
                    current_name = os.path.splitext(os.path.basename(self.image_url.name))[0]
                    new_filename = f"{current_name}.webp"
                    self.image_url.save(new_filename, ContentFile(output.read()), save=False)
            except Exception as e:
                print(f"WebP conversion failed: {e}")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.property.title}"

class Transaction(models.Model):
    class TypeEnum(models.TextChoices):
        PUBLICATION = 'PUBLICATION', _('Frais de Publication')
        BOOST = 'BOOST', _('Boost d\'Annonce')
        POPUP = 'POPUP', _('Mise en avant Pop-up')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TypeEnum.choices)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True, verbose_name=_("Référence FedaPay / Interne"))
    status = models.CharField(max_length=20, choices=[('PENDING', _('En attente')), ('SUCCESS', _('Réussite')), ('FAILED', _('Échec'))], default='PENDING')
    days = models.IntegerField(default=1, verbose_name=_("Nombre de jours"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions (Comptabilité)")

    def __str__(self):
        return f"{self.user} - {self.transaction_type} - {self.amount}F"

class PricingConfig(models.Model):
    # Publication
    publication_fee_rent = models.DecimalField(max_digits=20, decimal_places=0, default=0, verbose_name=_("Prix Publication (Location)"))
    publication_fee_sale = models.DecimalField(max_digits=20, decimal_places=0, default=0, verbose_name=_("Prix Publication (Vente)"))
    publication_fee_furnished = models.DecimalField(max_digits=20, decimal_places=0, default=0, verbose_name=_("Prix Publication (Meublé)"))
    
    # Boosts (Prix par jour)
    boost_daily_fee = models.DecimalField(max_digits=20, decimal_places=0, default=1000, verbose_name=_("Boost Standard (par jour)"))
    boost_popup_fee = models.DecimalField(max_digits=20, decimal_places=0, default=5000, verbose_name=_("Boost Pop-up (par jour)"))
    boost_infeed_fee = models.DecimalField(max_digits=20, decimal_places=0, default=3000, verbose_name=_("Boost In-Feed (par jour)"))
    boost_top_banner_fee = models.DecimalField(max_digits=20, decimal_places=0, default=7000, verbose_name=_("Boost Top Banner (par jour)"))

    class Meta:
        verbose_name = _("Paramètres des Tarifs")
        verbose_name_plural = _("Paramètres des Tarifs (DigitalH)")

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
    name = models.CharField(max_length=100, help_text=_("Ex: Réfrigérateur, Climatiseur, TV..."))
    brand = models.CharField(max_length=100, blank=True, null=True, help_text=_("Marque optionnelle"))
    icon_class = models.CharField(max_length=50, default='fa-plug', help_text=_("Icône FontAwesome (ex: fa-tv, fa-snowflake)"))
    
    def __str__(self):
        return f"{self.name} for {self.property.title}"


class PropertyReview(models.Model):
    """Avis et notation laissés sur une annonce par un locataire/acheteur."""
    RATING_CHOICES = [(i, f"{i} " + (_("étoile") if i == 1 else _("étoiles"))) for i in range(1, 6)]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Note (1-5)")
    title = models.CharField(max_length=120, blank=True, verbose_name="Titre de l'avis")
    comment = models.TextField(verbose_name="Commentaire")
    is_approved = models.BooleanField(default=False, verbose_name="Approuvé (visible)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('property', 'reviewer')
        ordering = ['-created_at']
        verbose_name = _("Avis")
        verbose_name_plural = _("Avis & Notations")

    def __str__(self):
        return f"{self.reviewer} → {self.property.title} ({self.rating}★)"


class PropertyAlert(models.Model):
    """Abonnement aux alertes email pour les nouvelles annonces."""
    email = models.EmailField(verbose_name=_("Email"))
    city = models.CharField(max_length=100, choices=CITY_CHOICES, blank=True, default='', verbose_name=_("Ville"))
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES, blank=True, default='', verbose_name=_("Type de bien"))
    listing_category = models.CharField(
        max_length=20,
        choices=[('', _('Toutes')), ('RENT', _('Location')), ('SALE', _('Vente')), ('FURNISHED', _('Meublé'))],
        blank=True, default='', verbose_name=_("Catégorie")
    )
    max_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name=_("Budget max (FCFA)"))
    token = models.CharField(max_length=64, unique=True, verbose_name=_("Token désabonnement"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Alerte Immobilière")
        verbose_name_plural = _("Alertes Immobilières (Abonnements)")

    def __str__(self):
        parts = [self.email]
        if self.city:
            parts.append(self.city)
        if self.property_type:
            parts.append(self.property_type)
        return " | ".join(parts)

    def save(self, *args, **kwargs):
        if not self.token:
            import secrets
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

class PropertyApplication(models.Model):
    """Candidature d'un locataire pour un bien spécifique."""
    class StatusEnum(models.TextChoices):
        PENDING = 'PENDING', _('En attente')
        ACCEPTED = 'ACCEPTED', _('Acceptée')
        REJECTED = 'REJECTED', _('Refusée')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='applications')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    message = models.TextField(blank=True, verbose_name="Message / Motivation")
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Candidature")
        verbose_name_plural = _("Candidatures")
        unique_together = ('property', 'tenant')

    def __str__(self):
        return f"Candidature de {self.tenant} pour {self.property.title}"
