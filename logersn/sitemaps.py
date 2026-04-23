from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Property

class PropertySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return Property.objects.filter(is_published=True).order_by('-created_at')

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return obj.get_absolute_url()

class StaticViewSitemap(Sitemap):
    protocol = 'https'
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
            'guide_courtiers'
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

class ProfessionalSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7
    protocol = 'https'

    def items(self):
        from users.models import User
        return User.objects.filter(is_verified_pro=True).order_by('-date_joined')

    def lastmod(self, obj):
        return obj.date_joined

    def location(self, obj):
        if obj.slug:
            return reverse('public_profile_slug', kwargs={'slug': obj.slug})
        return reverse('public_profile', kwargs={'user_id': obj.id})
