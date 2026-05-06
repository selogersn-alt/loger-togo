from .models import Advertisement, SEOSetting, SiteAnnouncement
from logersn.models import Property, PricingConfig

def ads_processor(request):
    """Make ads and announcements globally available in templates."""
    try:
        top_ads = Advertisement.objects.filter(location='TOP', is_active=True).order_by('-id')
        bottom_ads = Advertisement.objects.filter(location='BOTTOM', is_active=True).order_by('-id')
        popup_ads = Advertisement.objects.filter(location='POPUP', is_active=True).first()
        sidebar_ads = Advertisement.objects.filter(location='SIDEBAR', is_active=True).order_by('-id')
        in_feed_ads = Advertisement.objects.filter(location='BETWEEN_LISTINGS', is_active=True).order_by('-id')
        pop_under_ads = Advertisement.objects.filter(location='POP_UNDER', is_active=True).order_by('-id')
        sticky_footer_ads = Advertisement.objects.filter(location='STICKY_FOOTER', is_active=True).order_by('-id')
        property_popup = Property.objects.filter(is_featured_popup=True, is_published=True).order_by('-id').first()
        seo_settings = SEOSetting.objects.first()
        
        # Site Announcements
        announcements = SiteAnnouncement.objects.filter(is_active=True).order_by('-created_at')
        tickers = announcements.filter(announcement_type='TICKER')
        site_alerts = announcements.filter(announcement_type='POPUP')
        pricing_config = PricingConfig.objects.first()
    except Exception:
        top_ads = bottom_ads = sidebar_ads = in_feed_ads = pop_under_ads = sticky_footer_ads = []
        popup_ads = property_popup = seo_settings = tickers = site_alerts = pricing_config = None

    return {
        'ads_top': top_ads,
        'ads_bottom': bottom_ads,
        'ad_popup': popup_ads,
        'ad_pop_under': pop_under_ads,
        'ad_sticky_footer': sticky_footer_ads,
        'ads_sidebar': sidebar_ads,
        'ads_in_feed': in_feed_ads,
        'property_popup': property_popup,
        'seo_settings': seo_settings,
        'site_tickers': tickers,
        'site_alerts': site_alerts,
        'pricing': pricing_config,
    }
