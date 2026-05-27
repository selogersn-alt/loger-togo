from django import forms
from django.utils.translation import gettext_lazy as _
from .models import KYCProfile, User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

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
            'cni_front_image': _('Carte d\'identité (Recto)'),
            'cni_back_image': _('Carte d\'identité (Verso)'),
            'selfie_image': _('Selfie avec la carte'),
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('phone_number', 'email', 'role', 'company_name', 'coverage_area')
        widgets = {
            'phone_number': forms.TextInput(attrs={'id': 'phone', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'nom@exemple.com'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nom de votre agence (Optionnel)')}),
            'coverage_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ex: Lomé, Togo')}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields.pop('username')
        # On rend les champs non-obligatoires au niveau HTML pour la validation personnalisée
        self.fields['phone_number'].required = False
        self.fields['email'].required = False

        # Exclure SUB_ADMIN et CUSTOMER_SUPPORT du frontend
        if 'role' in self.fields:
            choices = self.fields['role'].choices
            self.fields['role'].choices = [
                choice for choice in choices 
                if choice[0] not in ['SUB_ADMIN', 'CUSTOMER_SUPPORT']
            ]

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone_number')
        email = cleaned_data.get('email')

        if not phone and not email:
            raise forms.ValidationError(_("Vous devez fournir soit un numéro de téléphone, soit une adresse email pour vous inscrire."))
        
        return cleaned_data

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('phone_number', 'email', 'role', 'is_verified_pro', 'company_name', 'coverage_area', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields.pop('username')
        
        if 'password' in self.fields:
            self.fields['password'].help_text = _("Le mot de passe est encrypté pour votre sécurité et n'est pas lisible en clair.")

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['company_name', 'email', 'profile_picture', 'slug', 'first_name', 'last_name', 'coverage_area', 'notification_preference']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);', 'placeholder': _('votre-nom-personnalise')}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);', 'accept': 'image/*'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
            'coverage_area': forms.TextInput(attrs={'class': 'form-control', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
            'notification_preference': forms.Select(attrs={'class': 'form-select', 'style': 'background-color: var(--bg-body); color: var(--text-main); border-color: var(--border-color);'}),
        }
        labels = {
            'company_name': _('Nom de l\'agence ou Entreprise'),
            'profile_picture': _('Logo ou Photo de profil'),
            'slug': _('Lien personnalisé (ex: Logertogo.com/p/votre-nom)'),
            'notification_preference': _('Mode de réception des notifications'),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            from django.utils.text import slugify
            slug = slugify(slug)
            if User.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(_("Ce lien personnalisé est déjà utilisé par un autre professionnel."))
        return slug
