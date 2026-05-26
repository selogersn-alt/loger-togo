from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class HotelStaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        # We index public/marketing pages of hotels subdomain
        return [
            'hotel_promo',
            'hotel_login',
            'hotel_register',
        ]

    def priority(self, item):
        return {
            'hotel_promo': 1.0,
            'hotel_login': 0.6,
            'hotel_register': 0.6
        }.get(item, 0.5)

    def changefreq(self, item):
        return {
            'hotel_promo': 'daily',
        }.get(item, 'monthly')

    def location(self, item):
        # Explicitly resolve using hotels urlconf
        return reverse(item, urlconf='logertogo.urls_hotel')
