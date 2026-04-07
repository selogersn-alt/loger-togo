from django import forms
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
        label="Photos du bien (Obligatoire, vous pouvez en sélectionner plusieurs)",
        required=True,
        widget=MultipleFileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    
    surface = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm2'}))
    bedrooms = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    toilets = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    total_rooms = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    has_garage = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    
    class Meta:
        model = Property
        fields = [
            'title', 'listing_category', 'property_type', 'city', 'neighborhood', 'price', 
            'price_per_night', 'surface', 'bedrooms', 'toilets', 'total_rooms', 'has_garage', 
            'description', 'wifi', 'swimming_pool', 'gym', 'air_conditioning',
            'refrigerator', 'washing_machine', 'microwave', 'tv_cable',
            'generator', 'water_tank'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Superbe appartement F4 vue mer...'}),
            'listing_category': forms.Select(attrs={'class': 'form-select'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'city': forms.Select(attrs={'class': 'form-select'}),
            'neighborhood': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 350000'}),
            'price_per_night': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 45000'}),
            'surface': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'm2'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'toilets': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_rooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'has_garage': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Décrivez le bien...'}),
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
        }
        labels = {
            'title': 'Titre de l\'annonce',
            'listing_category': 'Nature de l\'annonce',
            'property_type': 'Type de bien',
            'city': 'Ville',
            'neighborhood': 'Quartier',
            'price': 'Prix / Loyer mensuel (FCFA)',
            'price_per_night': 'Prix par nuitée (Meublé)',
            'description': 'Description détaillée',
            'wifi': 'WiFi',
            'swimming_pool': 'Piscine',
            'gym': 'Salle de sport',
            'air_conditioning': 'Climatisation',
            'refrigerator': 'Réfrigérateur',
            'washing_machine': 'Machine à laver',
            'microwave': 'Micro-ondes',
            'tv_cable': 'TV par câble',
            'generator': 'Groupe électrogène',
            'water_tank': 'Réservoir d\'eau',
        }
