from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Property

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        # Liste vos pages statiques principales (Accueil, Liste des biens...)
        return ['home', 'properties_list']

    def location(self, item):
        return reverse(item)

class PropertySitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        # Google indexera toutes vos annonces publiées
        return Property.objects.filter(is_published=True).order_by('-created_at')

    def lastmod(self, obj):
        # Date de dernière modification (ou création ici)
        return obj.created_at

    def location(self, obj):
        # Utilise le bloc dynamique du site pour pointer vers l'annonce
        return reverse('property_detail', args=[obj.id])
