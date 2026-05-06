from django.utils.translation import gettext as _
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from rest_framework import viewsets

from .models import Property, PropertyImage, Favorite, PropertyReview, PropertyAlert, PropertyApplication
from .forms import PropertyForm
from .serializers import PropertySerializer, PropertyImageSerializer
import json

# --- API ViewSets ---

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class PropertyImageViewSet(viewsets.ModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer

# --- HTML Views ---

def properties_list_view(request):
    city = request.GET.get('city')
    neighborhood = request.GET.get('neighborhood')
    property_type = request.GET.get('property_type')
    listing_category = request.GET.get('listing_category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    q = request.GET.get('q')
    
    properties = Property.objects.filter(is_published=True).select_related('owner').prefetch_related('images')
    
    # Filtres de base
    if listing_category and listing_category != 'ALL': properties = properties.filter(listing_category=listing_category)
    if property_type and property_type != 'ALL': properties = properties.filter(property_type=property_type)
    if min_price: properties = properties.filter(price__gte=int(float(min_price)))
    if max_price: properties = properties.filter(price__lte=int(float(max_price)))
    
    # Filtre textuel (recherche globale)
    if q:
        properties = properties.filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(neighborhood__icontains=q)
        )

    # Filtres géo
    if city and city != 'ALL': properties = properties.filter(city=city)
    
    # On garde une copie avant le filtre quartier pour le fallback
    pre_neighborhood_results = properties
    if neighborhood and neighborhood != 'ALL': 
        properties = properties.filter(neighborhood__icontains=neighborhood)
    
    # --- LOGIQUE DE SUGGESTION APPROXIMATIVE ---
    is_fallback = False
    if properties.count() == 0 and (neighborhood or q):
        # Si aucun résultat avec le quartier, on propose les résultats de la ville entière
        properties = pre_neighborhood_results
        is_fallback = True
        if properties.count() == 0:
            # Si toujours rien, on élargit encore (toutes les villes, même catégorie)
            properties = Property.objects.filter(is_published=True).select_related('owner').prefetch_related('images')
            if listing_category and listing_category != 'ALL':
                properties = properties.filter(listing_category=listing_category)
            properties = properties.order_by('-is_boosted', '-created_at')[:8]

    sort = request.GET.get('sort')
    if sort == 'price_asc': properties = properties.order_by('-is_boosted', 'price')
    elif sort == 'price_desc': properties = properties.order_by('-is_boosted', '-price')
    else: properties = properties.order_by('-created_at', '-is_boosted')
    
    # --- DONNÉES CARTE ---
    map_markers = []
    for p in properties:
        if p.latitude and p.longitude:
            main_img = p.get_main_image()
            map_markers.append({
                'id': str(p.id),
                'lat': float(p.latitude),
                'lng': float(p.longitude),
                'title': p.title,
                'price': int(p.price),
                'type': p.get_property_type_display(),
                'neighborhood': p.neighborhood,
                'category': p.listing_category,
                'url': p.get_absolute_url(),
                'img': main_img.image_url.url if main_img else None
            })

    context = {
        'properties': properties,
        'is_fallback': is_fallback,
        'search_query': q or neighborhood,
        'map_markers_json': json.dumps(map_markers),
        'breadcrumbs': [
            {'name': _('Annonces immobilières'), 'url': '/annonces/'}
        ]
    }
    return render(request, 'properties_list.html', context)

def property_detail_view(request, property_id=None, slug=None):
    if slug: property_obj = get_object_or_404(Property, slug=slug)
    else: property_obj = get_object_or_404(Property, id=property_id)
    
    property_obj.views_count += 1
    property_obj.save()
    
    is_favorite = request.user.is_authenticated and Favorite.objects.filter(user=request.user, property=property_obj).exists()
    related_properties = Property.objects.filter(city=property_obj.city, is_published=True).exclude(id=property_obj.id)[:4]
    
    return render(request, 'property_detail.html', {
        'property': property_obj, 
        'is_favorite': is_favorite, 
        'related_properties': related_properties,
        'breadcrumbs': [
            {'name': _('Annonces immobilières'), 'url': '/annonces/'},
            {'name': property_obj.title, 'url': property_obj.get_absolute_url()}
        ]
    })

from .constants import TOGO_NEIGHBORHOODS

@login_required
def create_property_view(request):
    if request.user.role == 'TENANT':
        messages.error(request, _("Accès pro requis."))
        return redirect('dashboard')
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                p = form.save(commit=False)
                p.owner = request.user
                p.save()
                
                images = request.FILES.getlist('images')
                for i, img in enumerate(images):
                    PropertyImage.objects.create(property=p, image_url=img, is_primary=(i == 0))
                
                messages.success(request, _("Votre annonce a été créée avec succès ! Elle est en attente de validation."))
                return redirect('initiate_payment', property_id=p.id, payment_type='PUBLICATION')
            except Exception as e:
                # Si erreur de stockage (S3), on garde l'annonce mais on log l'erreur
                print(f"Erreur d'enregistrement d'image: {e}")
                messages.warning(request, _("L'annonce a été créée, mais il y a eu un problème lors de l'envoi des images. Veuillez réessayer de les ajouter dans 'Modifier'."))
                return redirect('dashboard')
    else: 
        form = PropertyForm()
    return render(request, 'property_form.html', {'form': form, 'togo_neighborhoods': TOGO_NEIGHBORHOODS})

@login_required
def edit_property_view(request, property_id):
    p = get_object_or_404(Property, id=property_id, owner=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=p)
        if form.is_valid():
            p = form.save()
            # Ajout de nouvelles images si présentes
            images = request.FILES.getlist('images')
            if images:
                # On ne supprime pas les anciennes, on ajoute juste les nouvelles
                for img in images:
                    PropertyImage.objects.create(property=p, image_url=img)
            messages.success(request, _("Annonce modifiée avec succès !"))
            return redirect('/mon-compte/')
    else:
        form = PropertyForm(instance=p)
    return render(request, 'property_form.html', {
        'form': form, 'is_edit': True, 'property': p, 'togo_neighborhoods': TOGO_NEIGHBORHOODS
    })

@login_required
def delete_property_view(request, property_id):
    p = get_object_or_404(Property, id=property_id, owner=request.user)
    if request.method == 'POST': p.delete(); return redirect('/mon-compte/?section=ads')
    return render(request, 'confirm_delete.html', {'property': p, 'type': 'annonce'})

@login_required
def toggle_favorite_view(request, property_id):
    p = get_object_or_404(Property, id=property_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, property=p)
    if not created: fav.delete(); status = 'removed'
    else: status = 'added'
    return JsonResponse({'status': status})

@login_required
def submit_review_view(request, property_id):
    p = get_object_or_404(Property, id=property_id)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        PropertyReview.objects.create(property=p, reviewer=request.user, rating=rating, comment=comment)
        messages.success(request, _("Avis soumis !"))
    return redirect('property_detail', property_id=p.id)

def subscribe_alert_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        PropertyAlert.objects.create(email=email)
        messages.success(request, _("Alerte activée !"))
    return redirect('home')

def unsubscribe_alert_view(request, token):
    alert = get_object_or_404(PropertyAlert, token=token)
    alert.delete()
    messages.info(request, _("Alerte supprimée."))
    return redirect('home')

@login_required
def apply_to_property_view(request, property_id):
    """Permet au locataire de candidater pour un bien."""
    p = get_object_or_404(Property, id=property_id)
    if request.method == 'POST':
        message = request.POST.get('message', '')
        # Vérifier si déjà candidaté
        if PropertyApplication.objects.filter(property=p, tenant=request.user).exists():
            messages.warning(request, _("Vous avez déjà déposé votre candidature pour ce bien."))
        else:
            PropertyApplication.objects.create(
                property=p,
                tenant=request.user,
                message=message
            )
            messages.success(request, _("Votre candidature a été transmise au bailleur !"))
            
            # Optionnel : Initier une conversation chat
            from chat.models import Conversation
            conv, created = Conversation.objects.get_or_create(
                topic='PROPERTY_INQUIRY',
                related_property=p
            )
            if created:
                conv.participants.add(request.user, p.owner)
                
    return redirect(p.get_absolute_url())
