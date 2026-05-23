from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class AgenceStaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        # We index public/marketing pages of agence subdomain
        return [
            'agency_promo',
            'agency_login',
            'agency_register',
            'explications',
            'agency_privacy'
        ]

    def priority(self, item):
        return {
            'agency_promo': 1.0,
            'explications': 0.9,
            'agency_privacy': 0.8,
            'agency_login': 0.6,
            'agency_register': 0.6
        }.get(item, 0.5)

    def changefreq(self, item):
        return {
            'agency_promo': 'daily',
            'explications': 'weekly',
        }.get(item, 'monthly')

    def location(self, item):
        # Explicitly resolve using agence urlconf
        return reverse(item, urlconf='logertogo.urls_agence')
