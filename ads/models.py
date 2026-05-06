from django.db import models

class Advertisement(models.Model):
    AD_TYPE_CHOICES = [
        ('BANNER', 'Bannière Image'),
        ('SCRIPT', 'Code Script (Google Ads, etc)'),
    ]
    
    LOCATION_CHOICES = [
        ('TOP', 'Haut de page'),
        ('BOTTOM', 'Bas de page'),
        ('BETWEEN_LISTINGS', 'Entre les annonces (In-Feed)'),
        ('POPUP', 'Pop-up promotionnel'),
        ('POP_UNDER', 'Pop-under (Nouvel onglet)'),
        ('SIDEBAR', 'Barre latérale (Sidebar)'),
        ('STICKY_FOOTER', 'Barre flottante (Sticky Footer)'),
    ]

    title = models.CharField(max_length=255, verbose_name="Titre de la publicité")
    ad_type = models.CharField(max_length=10, choices=AD_TYPE_CHOICES, default='BANNER')
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, default='TOP')
    
    # Contenu pour les bannières
    image = models.ImageField(upload_to='ads/banners/', null=True, blank=True, verbose_name="Image de la bannière")
    target_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="Lien de redirection")
    
    # Contenu pour les scripts
    script_content = models.TextField(null=True, blank=True, verbose_name="Code Script / HTML")
    
    is_active = models.BooleanField(default=True, verbose_name="Publicité active")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_location_display()} - {self.title}"

    class Meta:
        verbose_name = "Publicité"
        verbose_name_plural = "Publicités"

class AdsConfig(models.Model):
    ads_txt_content = models.TextField(blank=True, verbose_name="Contenu du fichier ads.txt", help_text="Collez ici les lignes fournies par Google AdSense ou d'autres régies.")
    
    class Meta:
        verbose_name = "Configuration AdSense (ads.txt)"
        verbose_name_plural = "Configuration AdSense (ads.txt)"

class SEOSetting(models.Model):
    title = models.CharField(max_length=255, default="Paramètres SEO Globaux")
    header_scripts = models.TextField(blank=True, verbose_name="Scripts de l'en-tête (Head)", help_text="Google Analytics, Pixel Facebook, etc.")
    footer_scripts = models.TextField(blank=True, verbose_name="Scripts de pied de page (Body)", help_text="Scripts de chat, tracking, etc.")
    
    meta_description = models.TextField(blank=True, verbose_name="Méta Description par défaut")
    meta_keywords = models.CharField(max_length=500, blank=True, verbose_name="Méta Keywords")

    class Meta:
        verbose_name = "Paramètres SEO & Scripts"
        verbose_name_plural = "Paramètres SEO & Scripts"

    def __str__(self):
        return self.title

class SiteAnnouncement(models.Model):
    class TypeChoices(models.TextChoices):
        TICKER = 'TICKER', 'Bandeau défilant (Ticker)'
        POPUP = 'POPUP', 'Alerte Pop-up'
    
    title = models.CharField(max_length=255, verbose_name="Titre/Sujet")
    content = models.TextField(verbose_name="Contenu (Supporte HTML/JS)")
    announcement_type = models.CharField(max_length=10, choices=TypeChoices.choices, default=TypeChoices.TICKER)
    
    is_active = models.BooleanField(default=True, verbose_name="Activer l'annonce")
    background_color = models.CharField(max_length=20, default="#198754", verbose_name="Couleur de fond (Hex)")
    text_color = models.CharField(max_length=20, default="#ffffff", verbose_name="Couleur du texte (Hex)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Annonce du Site (Ticker/Alerte)"
        verbose_name_plural = "Annonces du Site (Ticker/Alerte)"

    def __str__(self):
        return f"{self.get_announcement_type_display()} - {self.title}"
