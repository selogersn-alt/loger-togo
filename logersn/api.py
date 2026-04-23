from django.db.models import Q
from rest_framework import viewsets, permissions, filters
from .models import Property, PropertyImage, Favorite
from users.models import User
from .serializers import PropertySerializer, PropertyImageSerializer, ProfessionalSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class ProfessionalsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Répertoire des agences et courtiers vérifiés.
    """
    queryset = User.objects.filter(
        Q(role='AGENCY') | Q(role='BROKER') | Q(role='AGENT')
    ).filter(is_active=True).order_by('-is_verified_pro', 'company_name')
    serializer_class = ProfessionalSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['company_name', 'first_name', 'last_name', 'coverage_area']

class PropertyViewSet(viewsets.ModelViewSet):
    """
    Guichet API pour visualiser et CREER des annonces.
    """
    serializer_class = PropertySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'neighborhood', 'description']

    def get_queryset(self):
        queryset = Property.objects.filter(is_published=True).order_by('-is_boosted', '-created_at')
        
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city=city)
            
        property_type = self.request.query_params.get('property_type')
        if property_type:
            queryset = queryset.filter(property_type=property_type)
            
        neighborhood = self.request.query_params.get('neighborhood')
        if neighborhood:
            queryset = queryset.filter(neighborhood__iexact=neighborhood)
            
        return queryset

    def get_permissions(self):
        if self.action in ['create', 'toggle_favorite', 'my_favorites']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # On définit l'utilisateur connecté comme propriétaire
        serializer.save(owner=self.request.user, is_published=True)

    @action(detail=True, methods=['post'], url_path='toggle-favorite')
    def toggle_favorite(self, request, pk=None):
        property_obj = self.get_object()
        favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
        if not created:
            favorite.delete()
            return Response({'status': 'removed'})
        return Response({'status': 'added'})

    @action(detail=False, methods=['get'], url_path='favorites')
    def my_favorites(self, request):
        favorites = Property.objects.filter(favorited_by__user=request.user)
        serializer = self.get_serializer(favorites, many=True)
        return Response(serializer.data)

class PropertyImageViewSet(viewsets.ModelViewSet):
    """
    API pour envoyer des images après la création de l'annonce.
    """
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
