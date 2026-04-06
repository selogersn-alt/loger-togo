from .models import Advertisement, SEOSetting
from logersn.models import Property

def ads_processor(request):
    """Make ads globally available in templates."""
    top_ads = Advertisement.objects.filter(location='TOP', is_active=True).order_by('?')
    bottom_ads = Advertisement.objects.filter(location='BOTTOM', is_active=True).order_by('?')
    popup_ads = Advertisement.objects.filter(location='POPUP', is_active=True).first()
    sidebar_ads = Advertisement.objects.filter(location='SIDEBAR', is_active=True).order_by('?')
    in_feed_ads = Advertisement.objects.filter(location='BETWEEN_LISTINGS', is_active=True).order_by('?')
    
    # Nouvelle source : Annonces immobilières boostées en Pop-up
    property_popup = Property.objects.filter(is_featured_popup=True, is_published=True).order_by('?').first()
    
    return {
        'ads_top': top_ads,
        'ads_bottom': bottom_ads,
        'ad_popup': popup_ads,
        'ads_sidebar': sidebar_ads,
        'ads_in_feed': in_feed_ads,
        'property_popup': property_popup,
        'seo_settings': SEOSetting.objects.first(),
    }
