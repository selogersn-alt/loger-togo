from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, KYCProfileViewSet, NILS_ProfileViewSet

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .api import UserMeView, RegisterView

router = DefaultRouter()
router.register(r'profiles', UserViewSet)
router.register(r'kyc', KYCProfileViewSet, basename='kyc')
router.register(r'nils', NILS_ProfileViewSet, basename='nils')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api_register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserMeView.as_view(), name='user_me'),
    path('', include(router.urls)),
]
