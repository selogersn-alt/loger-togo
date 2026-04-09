from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Property

class PropertySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Property.objects.all().order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse('property_detail', kwargs={'property_id': str(obj.id)})

class StaticViewSitemap(Sitemap):
    def items(self):
        return [
            'home', 
            'about', 
            'properties_list', 
            'professionals_list',
            'cgu',
            'privacy',
            'guide_locataires',
            'guide_bailleurs',
            'guide_agences',
            'guide_courtiers',
            'fraud_list'
        ]

    def priority(self, item):
        return {
            'home': 1.0,
            'properties_list': 0.8,
            'guide_locataires': 0.7,
            'guide_bailleurs': 0.7,
        }.get(item, 0.5)

    def changefreq(self, item):
        return {
            'home': 'daily',
            'properties_list': 'daily',
        }.get(item, 'weekly')

    def location(self, item):
        return reverse(item)
