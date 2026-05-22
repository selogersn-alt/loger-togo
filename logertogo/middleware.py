class SubdomainURLRoutingMiddleware:
    """
    Middleware to dynamically route subdomain requests.
    If host starts with 'agence.', we override urlconf to use 'logertogo.urls_agence'.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower()
        if host.startswith('agence.'):
            request.urlconf = 'logertogo.urls_agence'
        return self.get_response(request)
