from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from management import views_agency

from django.contrib.sitemaps.views import sitemap
from logersn.sitemaps_agence import AgenceStaticSitemap

sitemaps = {
    'agence_static': AgenceStaticSitemap,
}

urlpatterns = [
    path('', views_agency.agency_promo, name='agency_promo'),
    path('dashboard/', views_agency.agency_dashboard, name='agency_dashboard'),
    path('explications/', views_agency.explications_view, name='explications'),
    path('confidentialite/', views_agency.agency_privacy_view, name='agency_privacy'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('connexion/', views_agency.agency_login, name='agency_login'),
    path('inscription/', views_agency.agency_register, name='agency_register'),
    path('deconnexion/', views_agency.agency_logout, name='agency_logout'),
    path('clients/', views_agency.agency_clients, name='agency_clients'),
    path('pipeline/', views_agency.agency_pipeline, name='agency_pipeline'),
    path('pipeline/update-stage/', views_agency.agency_update_pipeline_stage, name='agency_update_pipeline_stage'),
    path('baux/', views_agency.agency_leases, name='agency_leases'),
    path('paiements/', views_agency.agency_payments, name='agency_payments'),
    path('quittance/<uuid:payment_id>/', views_agency.agency_receipt, name='agency_receipt'),
    path('biens/', views_agency.agency_properties, name='agency_properties'),
    path('biens/nouveau/', views_agency.agency_property_create, name='agency_property_create'),
    path('biens/<uuid:property_id>/modifier/', views_agency.agency_property_edit, name='agency_property_edit'),
    path('biens/<uuid:property_id>/publication/', views_agency.agency_property_toggle_publication, name='agency_property_toggle_publication'),
]

# Ensure static & media urls work under the subdomain as well
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'management.views_agency.agency_404_handler'
handler500 = 'management.views_agency.agency_500_handler'

