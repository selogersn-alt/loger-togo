from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Property

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class PropertyForm(forms.ModelForm):
    images = MultipleFileField(
        label=_("Photos du bien (Sélectionnez une ou plusieurs images)"),
        required=True,
        widget=MultipleFileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si on modifie un bien existant, les photos ne sont plus obligatoires
        if self.instance and self.instance.pk:
            self.fields['images'].required = False
    
    surface = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm2'}))
    bedrooms = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    toilets = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    total_rooms = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    salons = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    kitchens = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    households = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    floor_level = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    has_garage = forms.BooleanField(required=False, label=_("Garage / Parking"), widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    has_balcony = forms.BooleanField(required=False, label=_("Balcon"), widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    has_terrace = forms.BooleanField(required=False, label=_("Terrasse"), widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    has_courtyard = forms.BooleanField(required=False, label=_("Cour"), widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    has_garden = forms.BooleanField(required=False, label=_("Jardin"), widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    def clean(self):
        cleaned_data = super().clean()
        
        # NETTOYAGE LASER STRICT ABSOLU : On liste explicitement a-z et 0-9. Le \w est banni car il laissait passer les "sélecteurs de variations" invisibles.
        import re
        safe_chars_regex = r'[^a-zA-Z0-9\s.,;:!?\'"()\-@€$£%+=/\\&*_°ÂÀÄÇÉÈÊËÎÏÔÖÙÛÜâàäçéèêëîïôöùûü\r\n]'
        
        desc = cleaned_data.get('description', '')
        if desc:
            cleaned_data['description'] = re.sub(safe_chars_regex, '', desc)
            
        title = cleaned_data.get('title', '')
        if title:
            cleaned_data['title'] = re.sub(safe_chars_regex, '', title)

        # Remplacer None par 0 pour les champs Integer
        integer_fields = [
            'surface', 'bedrooms', 'toilets', 'total_rooms', 'salons', 'kitchens', 'households', 'floor_level',
            'deposit_months', 'advance_months', 'agency_fee_months', 'visit_fee'
        ]
        for field in integer_fields:
            if cleaned_data.get(field) is None:
                cleaned_data[field] = 0

        # Logique de cohérence par catégorie (Conflits de logique)
        listing_category = cleaned_data.get('listing_category')
        
        # 1. Pour les meublés, le prix par nuitée est optionnel
        if listing_category != 'FURNISHED':
            cleaned_data['price_per_night'] = None

        # 2. Conditions de location (Applicable si location classique OU meublé)
        if listing_category not in ['RENT', 'FURNISHED']:
            cleaned_data['deposit_months'] = 0
            cleaned_data['advance_months'] = 0
            cleaned_data['agency_fee_months'] = 0

        # 3. Le type de document est fortement recommandé pour les ventes, mais on autorise "Aucun/Autre"
        if listing_category == 'SALE':
            doc_type = cleaned_data.get('document_type')
            if not doc_type:
                # On ne bloque plus si c'est 'NONE', seulement si c'est vide
                self.add_error('document_type', _("Veuillez préciser le type de document (même si Aucun)."))
        
        return cleaned_data
    
    class Meta:
        model = Property
        fields = [
            'title', 'listing_category', 'property_type', 'document_type', 'city', 'neighborhood', 'price', 
            'price_per_night', 'surface', 'bedrooms', 'toilets', 'total_rooms', 'salons', 'kitchens', 'households', 'floor_level',
            'has_garage', 'has_balcony', 'has_terrace', 'has_courtyard', 'has_garden',
            'description', 'wifi', 'swimming_pool', 'gym', 'air_conditioning',
            'refrigerator', 'washing_machine', 'microwave', 'tv_cable',
            'generator', 'water_tank',
            'latitude', 'longitude',
            'discount_percentage', 'discount_price',
            'deposit_months', 'advance_months', 'agency_fee_months', 'visit_fee',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ex: Superbe appartement F4 vue mer...')}),
            'listing_category': forms.Select(attrs={'class': 'form-select'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ex: Adidogomé')}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Ex: 350000')}),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Ex: 45000')}),
            'deposit_months': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Ex: 3')}),
            'advance_months': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Ex: 10')}),
            'agency_fee_months': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Ex: 1')}),
            'visit_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Ex: 5000')}),
            'surface': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('m2')}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'toilets': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'salons': forms.NumberInput(attrs={'class': 'form-control'}),
            'kitchens': forms.NumberInput(attrs={'class': 'form-control'}),
            'households': forms.NumberInput(attrs={'class': 'form-control'}),
            'floor_level': forms.NumberInput(attrs={'class': 'form-control'}),
            'has_garage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('Décrivez le bien...')}),
            'wifi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'swimming_pool': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gym': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'air_conditioning': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'refrigerator': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'washing_machine': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'microwave': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tv_cable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'generator': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'water_tank': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
        labels = {
            'title': _("Titre de l'annonce"),
            'listing_category': _("Nature de l'annonce"),
            'property_type': _("Type de bien"),
            'city': _("Ville"),
            'neighborhood': _("Quartier"),
            'document_type': _("Nom du papier administratif (Obligatoire pour les ventes)"),
            'price': _("Prix / Loyer mensuel (FCFA)"),
            'price_per_night': _("Prix par nuitée (Meublé)"),
            'description': _("Description détaillée"),
            'wifi': _("WiFi"),
            'swimming_pool': _("Piscine"),
            'gym': _("Salle de sport"),
            'air_conditioning': _("Climatisation"),
            'refrigerator': _("Réfrigérateur"),
            'washing_machine': _("Machine à laver"),
            'microwave': _("Micro-ondes"),
            'tv_cable': _("TV par câble"),
            'generator': _("Groupe électrogène"),
            'water_tank': _("Réservoir d'eau"),
            'households': _("Nombre de ménages"),
            'floor_level': _("Niveau d'étage"),
            'has_garage': _("Garage / Parking"),
            'has_balcony': _("Balcon"),
            'has_terrace': _("Terrasse"),
            'has_courtyard': _("Cour"),
            'has_garden': _("Jardin"),
            'discount_percentage': _("Pourcentage de remise (%)"),
            'discount_price': _("Prix final après remise (FCFA)"),
            'deposit_months': _("Nombre de mois de caution"),
            'advance_months': _("Nombre de mois d'avance"),
            'agency_fee_months': _("Frais d'agence (en mois)"),
            'visit_fee': _("Frais de visite (FCFA)"),
            'salons': _("Nombre de salons"),
            'kitchens': _("Nombre de cuisines"),
        }
