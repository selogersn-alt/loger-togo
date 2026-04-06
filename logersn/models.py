import uuid
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

from .constants import PROPERTY_TYPE_CHOICES, CITY_CHOICES, NEIGHBORHOOD_CHOICES

class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    description = models.TextField()
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    city = models.CharField(max_length=100, choices=CITY_CHOICES, default='DAKAR')
    neighborhood = models.CharField(max_length=100, choices=NEIGHBORHOOD_CHOICES)
    rent_price = models.DecimalField(max_digits=12, decimal_places=2)
    surface = models.IntegerField(default=0, blank=True, verbose_name="Surface (m2)")
    bedrooms = models.IntegerField(default=0, blank=True, verbose_name="Nombre de chambres")
    toilets = models.IntegerField(default=0, blank=True, verbose_name="Nombre de toilettes")
    total_rooms = models.IntegerField(default=1, blank=True, verbose_name="Nombre total de pièces")
    has_garage = models.BooleanField(default=False, blank=True, verbose_name="Garage disponible")
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
    amount = models.DecimalField(max_digits=10, decimal_places=2)
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
    publication_fee = models.DecimalField(max_digits=10, decimal_places=2, default=100.00, verbose_name="Prix Publication")
    boost_daily_fee = models.DecimalField(max_digits=10, decimal_places=2, default=100.00, verbose_name="Prix Boost par jour")
    popup_daily_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00, verbose_name="Prix Pop-up par jour")

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
