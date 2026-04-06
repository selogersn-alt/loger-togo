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
        ('SIDEBAR', 'Barre latérale (Sidebar)'),
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
