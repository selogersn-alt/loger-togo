from rest_framework import serializers
from .models import User, KYCProfile, NILS_Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone_number', 'first_name', 'last_name', 
            'company_name', 'user_type', 'city', 'role', 'is_verified',
            'is_active', 'is_staff', 'date_joined'
        ]

class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number', 
            'company_name', 'user_type', 'city', 'role', 'is_verified'
        ]

class KYCProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCProfile
        fields = '__all__'

class NILS_ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NILS_Profile
        fields = '__all__'
