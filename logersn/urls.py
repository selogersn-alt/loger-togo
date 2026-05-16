from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, PropertyImageViewSet, request_visit_view, visit_success_view, submit_review_view

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'images', PropertyImageViewSet, basename='propertyimage')

urlpatterns = [
    path('', include(router.urls)),
    path('biens/<uuid:property_id>/visite/', request_visit_view, name='request_visit'),
    path('visite/succes/<uuid:visit_id>/', visit_success_view, name='visit_success'),
    path('biens/<uuid:property_id>/avis/', submit_review_view, name='submit_review'),
]
