from rest_framework import serializers
from .models import User, KYCProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone_number', 'first_name', 'last_name', 
            'company_name', 'role', 'is_verified_pro',
            'is_active', 'is_staff', 'date_joined'
        ]

class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number', 
            'company_name', 'role', 'is_verified_pro'
        ]

class KYCProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCProfile
        fields = '__all__'

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'company_name', 'profile_picture']
