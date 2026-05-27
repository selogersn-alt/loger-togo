from rest_framework import serializers
from .models import Property, PropertyImage
from users.models import User

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'property', 'image_url', 'is_primary']

class LogersnUserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'company_name', 'phone_number', 'is_verified_pro', 'profile_picture']

class ProfessionalSerializer(serializers.ModelSerializer):
    properties_count = serializers.IntegerField(source='properties.count', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'company_name', 'phone_number', 'email', 
            'role', 'is_verified_pro', 'profile_picture', 'coverage_area', 
            'slug', 'properties_count'
        ]

class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    owner = LogersnUserMiniSerializer(read_only=True)
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    listing_category_display = serializers.CharField(source='get_listing_category_display', read_only=True)
    absolute_url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'slug', 'description', 'price', 'price_per_night', 
            'city', 'neighborhood', 'property_type', 'property_type_display',
            'listing_category', 'listing_category_display', 'bedrooms', 
            'toilets', 'total_rooms', 'salons', 'kitchens', 'surface',
            'has_garage', 'has_balcony', 'has_terrace', 'has_courtyard', 'has_garden',
            'document_type', 'is_boosted', 'created_at', 
            'images', 'owner', 'absolute_url'
        ]
