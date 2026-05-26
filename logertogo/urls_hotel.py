from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from management import views_hotel
from django.contrib.sitemaps.views import sitemap
from logersn.sitemaps_hotel import HotelStaticSitemap

sitemaps = {
    'hotel_static': HotelStaticSitemap,
}

urlpatterns = [
    path('', views_hotel.hotel_promo, name='hotel_promo'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('connexion/', views_hotel.hotel_login, name='hotel_login'),
    path('inscription/', views_hotel.hotel_register, name='hotel_register'),
    path('deconnexion/', views_hotel.hotel_logout, name='hotel_logout'),
    path('dashboard/', views_hotel.hotel_dashboard, name='hotel_dashboard'),
    
    # Rooms Management
    path('chambres/', views_hotel.hotel_rooms, name='hotel_rooms'),
    path('chambres/nouveau/', views_hotel.hotel_room_create, name='hotel_room_create'),
    path('chambres/<uuid:room_id>/modifier/', views_hotel.hotel_room_edit, name='hotel_room_edit'),
    path('chambres/<uuid:room_id>/statut/', views_hotel.hotel_room_toggle_status, name='hotel_room_toggle_status'),
    
    # Bookings & POS (Point of Sale/Consommations) Management
    path('reservations/', views_hotel.hotel_bookings, name='hotel_bookings'),
    path('reservations/nouveau/', views_hotel.hotel_booking_create, name='hotel_booking_create'),
    path('reservations/<uuid:booking_id>/', views_hotel.hotel_booking_detail, name='hotel_booking_detail'),
    path('reservations/<uuid:booking_id>/checkin/', views_hotel.hotel_booking_checkin, name='hotel_booking_checkin'),
    path('reservations/<uuid:booking_id>/checkout/', views_hotel.hotel_booking_checkout, name='hotel_booking_checkout'),
    path('reservations/<uuid:booking_id>/add-charge/', views_hotel.hotel_booking_add_charge, name='hotel_booking_add_charge'),
    
    # Profile / Establishment Settings
    path('profil/', views_hotel.hotel_profile, name='hotel_profile'),
    
    # Visual Planning & Analytics
    path('planning/', views_hotel.hotel_planning, name='hotel_planning'),
    path('analyses/', views_hotel.hotel_analytics, name='hotel_analytics'),
    
    # Shifts & Reception Cash Register
    path('shifts/', views_hotel.hotel_shifts, name='hotel_shifts'),
    path('shifts/ouvrir/', views_hotel.hotel_shift_open, name='hotel_shift_open'),
    path('shifts/<uuid:shift_id>/cloturer/', views_hotel.hotel_shift_close, name='hotel_shift_close'),
    
    # Collaborators / Sub-agents Management
    path('collaborateurs/', views_hotel.hotel_sub_agents, name='hotel_sub_agents'),
    path('collaborateurs/<uuid:agent_id>/supprimer/', views_hotel.hotel_sub_agent_delete, name='hotel_sub_agent_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'management.views_hotel.hotel_404_handler'
handler500 = 'management.views_hotel.hotel_500_handler'
