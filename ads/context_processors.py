from .models import Advertisement, SEOSetting
from logersn.models import Property

def ads_processor(request):
    """Make ads globally available in templates."""
    try:
        top_ads = Advertisement.objects.filter(location='TOP', is_active=True).order_by('-id')
        bottom_ads = Advertisement.objects.filter(location='BOTTOM', is_active=True).order_by('-id')
        popup_ads = Advertisement.objects.filter(location='POPUP', is_active=True).first()
        sidebar_ads = Advertisement.objects.filter(location='SIDEBAR', is_active=True).order_by('-id')
        in_feed_ads = Advertisement.objects.filter(location='BETWEEN_LISTINGS', is_active=True).order_by('-id')
        property_popup = Property.objects.filter(is_featured_popup=True, is_published=True).order_by('-id').first()
        seo_settings = SEOSetting.objects.first()
    except Exception:
        top_ads = bottom_ads = sidebar_ads = in_feed_ads = []
        popup_ads = property_popup = seo_settings = None

    return {
        'ads_top': top_ads,
        'ads_bottom': bottom_ads,
        'ad_popup': popup_ads,
        'ads_sidebar': sidebar_ads,
        'ads_in_feed': in_feed_ads,
        'property_popup': property_popup,
        'seo_settings': seo_settings,
    }
