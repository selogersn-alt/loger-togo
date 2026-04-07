from django import forms
from .models import KYCProfile

class KYCProfileForm(forms.ModelForm):
    class Meta:
        model = KYCProfile
        fields = ['cni_front_image', 'cni_back_image', 'selfie_image']
        widgets = {
            'cni_front_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'cni_back_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'selfie_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }
        labels = {
            'cni_front_image': 'Carte d\'identité (Recto)',
            'cni_back_image': 'Carte d\'identité (Verso)',
            'selfie_image': 'Selfie avec la carte',
        }

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('phone_number', 'email', 'role', 'company_name', 'coverage_area')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # S'assurer que le champ username est géré correctement par form.save()
        if 'username' in self.fields:
            self.fields.pop('username')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('phone_number', 'email', 'role', 'is_verified_pro', 'company_name', 'coverage_area', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields.pop('username')
        
        # Personnalisation de l'aide pour le mot de passe en français
        if 'password' in self.fields:
            self.fields['password'].help_text = "Le mot de passe est encrypté pour votre sécurité et n'est pas lisible en clair."
