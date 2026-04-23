"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from logersn.sitemaps import StaticViewSitemap, PropertySitemap, ProfessionalSitemap

from rest_framework.routers import DefaultRouter
from logersn.api import PropertyViewSet, PropertyImageViewSet, ProfessionalsViewSet
from chat.api import ConversationViewSet
from users.api import SolvencyDocumentViewSet

# API Router configuration
router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='api-property')
router.register(r'property-images', PropertyImageViewSet, basename='api-property-image')
router.register(r'professionals', ProfessionalsViewSet, basename='api-professional')
router.register(r'conversations', ConversationViewSet, basename='api-conversation')
router.register(r'solvency-documents', SolvencyDocumentViewSet, basename='api-solvency-doc')


sitemaps = {
    'static': StaticViewSitemap,
    'properties': PropertySitemap,
    'professionals': ProfessionalSitemap,
}
from .views import (
    home_view, properties_list_view, property_detail_view, 
    login_view, register_view, logout_view, 
    dashboard_view, create_property_view, send_message_view,
    initiate_chat_view, start_support_view, verify_phone_view,
    kyc_submit_view, about_view, verified_professionals_view,
    public_profile_view, update_profile_view,
    edit_property_view, delete_property_view,
    initiate_payment_view, checkout_payment_view, payment_callback_view, payment_success_view, 
    password_recovery_view, password_reset_confirm_view, admin_generate_reset_link,
    cgu_view, privacy_view, toggle_favorite_view, chat_poll_view,
    guide_locataires_view, guide_bailleurs_view, guide_agences_view, guide_courtiers_view,
    submit_review_view, subscribe_alert_view, unsubscribe_alert_view,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from ads.views import ads_txt_view  # Certification Google
from .admin_views import admin_statistics_view, admin_marketing_email_view
from django.conf.urls import handler404, handler500

handler404 = 'logertogo.views.custom_404_view'
handler500 = 'logertogo.views.custom_500_view'

urlpatterns = [
    path('', home_view, name='home'),
    path('a-propos/', about_view, name='about'),
    path('professionnels/', verified_professionals_view, name='professionals_list'),
    path('agences/', lambda r: redirect('professionals_list')), # Aliasing legacy URL from Menu

    path('admin/statistiques/', admin_statistics_view, name='admin_statistics'), # Custom Admin Route
    path('admin/campagne-email/', admin_marketing_email_view, name='admin_marketing_email'),
    
    # API Routes
    path('api/', include(router.urls)),
    
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/logersn/', include('logersn.urls')),

    path('annonces/nouvelle/', create_property_view, name='create_property'),
    path('annonces/', properties_list_view, name='properties_list'),
    path('annonces/<uuid:property_id>/', property_detail_view, name='property_detail'),
    path('annonces/<slug:slug>/', property_detail_view, name='property_detail_slug'),
    path('annonces/<uuid:property_id>/modifier/', edit_property_view, name='edit_property'),
    path('annonces/<uuid:property_id>/supprimer/', delete_property_view, name='delete_property'),
    path('annonces/<uuid:property_id>/avis/', submit_review_view, name='submit_review'),
    
    # Certification Ads (Google AdSense)
    path('ads.txt', ads_txt_view, name='ads_txt'),
    
    # Alertes
    path('alertes/s-abonner/', subscribe_alert_view, name='subscribe_alert'),
    path('alertes/desabonner/<str:token>/', unsubscribe_alert_view, name='unsubscribe_alert'),

    path('profil/verification-telephonique/', verify_phone_view, name='verify_phone'),
    path('mon-compte/', dashboard_view, name='dashboard'),
    path('chat/start/<uuid:property_id>/', initiate_chat_view, name='initiate-chat'),
    path('chat/support/', start_support_view, name='support-chat'),
    path('chat/send/<uuid:conversation_id>/', send_message_view, name='send-message'),
    path('chat/send/', send_message_view, name='send-message-new'),
    path('profil/kyc/soumettre/', kyc_submit_view, name='kyc_submit'),

    path('connexion/', login_view, name='login'),
    path('inscription/', register_view, name='register'),
    path('deconnexion/', logout_view, name='logout'),

    path('verifier-telephone/', verify_phone_view, name='verify_phone'),
    path('profil-public/<uuid:user_id>/', public_profile_view, name='public_profile'),
    path('p/<slug:slug>/', public_profile_view, name='public_profile_slug'),
    path('mon-compte/profil/modifier/', update_profile_view, name='update_profile'),
    path('recuperation-compte/', password_recovery_view, name='password_recovery'),
    path('reinitialiser-mot-de-passe/<uidb64>/<token>/', password_reset_confirm_view, name='password_reset_confirm_public'),
    path('admin/generer-lien-reset/<uuid:user_id>/', admin_generate_reset_link, name='admin_generate_reset_link'),

    # Moteur de Paiement DigitalH
    path('paiement/configurer/<uuid:property_id>/<str:payment_type>/', checkout_payment_view, name='checkout_payment'),
    path('paiement/initier/<uuid:property_id>/<str:payment_type>/', initiate_payment_view, name='initiate_payment'),
    path('paiement/callback/', payment_callback_view, name='payment_callback'),
    path('payments/callback/', payment_callback_view), # Alias international pour éviter les 404
    path('paiement/succes/<uuid:transaction_id>/', payment_success_view, name='payment_success'),
    
    # Nouvelles Routes UX & Légal
    path('cgu/', cgu_view, name='cgu'),
    path('confidentialite/', privacy_view, name='privacy'),
    path('favori/basculer/<uuid:property_id>/', toggle_favorite_view, name='toggle_favorite'),
    path('chat/poll/<uuid:conversation_id>/', chat_poll_view, name='chat-poll'),
    
    # Nouvelles Routes Signalement & Solvabilité

    
    # Guides d'utilisation
    path('guide/locataires/', guide_locataires_view, name='guide_locataires'),
    path('guide/bailleurs/', guide_bailleurs_view, name='guide_bailleurs'),
    path('guide/agences/', guide_agences_view, name='guide_agences'),
    path('guide/courtiers/', guide_courtiers_view, name='guide_courtiers'),
    
    # API Documentation (Point 8)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Sitemap & SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),

    # ---- PWA (Progressive Web App) ----
    path('manifest.json', TemplateView.as_view(
        template_name='pwa/manifest.json',
        content_type='application/json'
    ), name='pwa-manifest'),
    path('sw.js', TemplateView.as_view(
        template_name='pwa/sw.js',
        content_type='application/javascript'
    ), name='pwa-sw'),
]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
