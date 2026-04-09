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

class SolvencyDocumentForm(forms.ModelForm):
    class Meta:
        from .models import SolvencyDocument
        model = SolvencyDocument
        fields = ['doc_type', 'file']
        labels = {
            'doc_type': 'Type de document',
            'file': 'Fichier (PDF ou Image)'
        }
        widgets = {
            'doc_type': forms.Select(attrs={'class': 'form-select', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
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
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['company_name', 'email', 'profile_picture', 'slug', 'first_name', 'last_name', 'coverage_area']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);', 'placeholder': 'votre-nom-personnalise'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);', 'accept': 'image/*'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
            'coverage_area': forms.TextInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
        }
        labels = {
            'company_name': 'Nom de l\'agence ou Entreprise',
            'profile_picture': 'Logo ou Photo de profil',
            'slug': 'Lien personnalisé (ex: logersenegal.com/p/votre-nom)',
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            from django.utils.text import slugify
            slug = slugify(slug)
            # Vérifier l'unicité en excluant l'utilisateur actuel
            if User.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Ce lien personnalisé est déjà utilisé par un autre professionnel.")
        return slug
