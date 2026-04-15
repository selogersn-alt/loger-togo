from rest_framework import serializers
from .models import Property, PropertyImage
from users.models import User

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'property', 'image_url', 'is_primary']

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'company_name', 'phone_number']

class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    owner = UserMiniSerializer(read_only=True)
    property_type_display = serializers.CharField(source='get_property_type_display', read_only=True)
    listing_category_display = serializers.CharField(source='get_listing_category_display', read_only=True)
    absolute_url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'slug', 'description', 'price', 'price_per_night', 
            'city', 'neighborhood', 'property_type', 'property_type_display',
            'listing_category', 'listing_category_display', 'bedrooms', 
            'toilets', 'surface', 'is_boosted', 'created_at', 
            'images', 'owner', 'absolute_url'
        ]
