def google_maps_api_key(request):
    """
    Injecte la clé API Google Maps dans tous les templates.
    """
    from django.conf import settings
    return {
        'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
    }
