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
        ACTE_COUTUMIER = 'ACTE_COUTUMIER', _('Acte Coutumier')
        DEUX_TAMPONS = 'DEUX_TAMPONS', _('2 Tampons')
        TROIS_TAMPONS = 'TROIS_TAMPONS', _('3 Tampons')

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
    
    # Conditions de location (Location)
    deposit_months = models.IntegerField(default=0, blank=True, null=True, verbose_name=_("Mois de caution"))
    advance_months = models.IntegerField(default=0, blank=True, null=True, verbose_name=_("Mois d'avance"))
    agency_fee_months = models.IntegerField(default=0, blank=True, null=True, verbose_name=_("Mois de frais d'agence"))
    visit_fee = models.IntegerField(default=0, blank=True, null=True, verbose_name=_("Frais de visite (CFA)"))

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
    
    # Tarification Dynamique (Meublés)
    discount_percentage = models.PositiveIntegerField(default=0, verbose_name=_("Remise (%)"))
    discount_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name=_("Prix après remise (CFA)"))
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['listing_category', 'is_published']),
            models.Index(fields=['property_type']),
            models.Index(fields=['city', 'neighborhood']),
            models.Index(fields=['is_boosted']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.slug:
            return reverse('property_detail_slug', kwargs={'slug': self.slug})
        return reverse('property_detail', kwargs={'property_id': self.id})

    def save(self, *args, **kwargs):
        # Calcul automatique du prix remisé (Senior Logic)
        if self.discount_percentage > 0 and self.price > 0:
            reduction = (self.price * self.discount_percentage) / 100
            self.discount_price = self.price - reduction
        elif not self.discount_price:
            self.discount_price = self.price

        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = "propriete"
            # On ajoute une partie de l'ID pour garantir l'unicité absolue
            self.slug = f"{base_slug}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)

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

    @property
    def get_main_image(self):
        """Retourne l'image principale ou la première image, sinon un placeholder."""
        try:
            main_img = self.images.filter(is_primary=True).first() or self.images.first()
            if main_img and main_img.image_url:
                return main_img.image_url.url
        except Exception:
            pass
        # Placeholder neutre et professionnel aux couleurs de la marque
        return "https://images.unsplash.com/photo-1582407947304-fd86f028f716?q=80&w=1000&auto=format&fit=crop"

class PropertyImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image_url = models.FileField(upload_to='properties/')
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Optimisation WebP en mémoire avant l'upload vers R2/S3
        if not self.pk and self.image_url:
            try:
                from PIL import Image
                import io
                from django.core.files.base import ContentFile
                
                # Ouvrir l'image
                img = Image.open(self.image_url)
                
                # Si ce n'est pas déjà du WebP, on convertit
                if img.format != 'WEBP':
                    output = io.BytesIO()
                    # Convertir en RGB si nécessaire (pour JPEG/PNG avec alpha vers WebP)
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    img.save(output, format='WEBP', quality=80)
                    output.seek(0)
                    
                    # Nouveau nom de fichier
                    name = self.image_url.name.split('.')[0] + '.webp'
                    
                    # Remplacement du fichier original par la version optimisée
                    # On utilise ContentFile pour que Django l'uploade lors du super().save()
                    self.image_url = ContentFile(output.read(), name=name)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Image optimization skipped: {e}")

        # Upload effectif vers le stockage (Local ou R2/S3)
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"CRITICAL: Failed to upload to storage (R2/S3?): {e}")
            # On ne relance pas pour éviter le crash 500, mais l'annonce n'aura pas cette image.
            # Cependant, nous avons corrigé la configuration R2 pour que cela n'arrive plus.

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

class PropertyAvailability(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='availabilities')
    start_date = models.DateField()
    end_date = models.DateField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _("Disponibilité")
        verbose_name_plural = _("Disponibilités")

class Reservation(models.Model):
    class StatusEnum(models.TextChoices):
        PENDING = 'PENDING', _('En attente')
        CONFIRMED = 'CONFIRMED', _('Confirmée')
        CANCELLED = 'CANCELLED', _('Annulée')
        COMPLETED = 'COMPLETED', _('Terminée')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Réservation")
        verbose_name_plural = _("Réservations")

class VisitRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='visit_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visit_requests')
    proposed_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Reservation.StatusEnum.choices, default=Reservation.StatusEnum.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Demande de visite")
        verbose_name_plural = _("Demandes de visite")
