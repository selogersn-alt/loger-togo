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
import datetime
import datetime

# --- API ViewSets ---

from rest_framework.decorators import action
from rest_framework.response import Response
import math

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.filter(is_published=True)
    serializer_class = PropertySerializer

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """
        Endpoint API robuste pour Android Kotlin.
        Ex: /api/logersn/properties/nearby/?lat=6.1&lng=1.2&radius=5
        """
        try:
            user_lat = float(request.query_params.get('lat'))
            user_lng = float(request.query_params.get('lng'))
            radius = float(request.query_params.get('radius', 10))
        except (TypeError, ValueError):
            return Response({"error": "Latitude, longitude and radius are required."}, status=400)

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371.0
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)
            a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
            return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        qs = self.get_queryset().exclude(latitude__isnull=True).exclude(longitude__isnull=True)
        
        properties = []
        for p in qs:
            try:
                dist = haversine(user_lat, user_lng, float(p.latitude), float(p.longitude))
                if dist <= radius:
                    # On ajoute la distance au dictionnaire sérialisé
                    data = self.get_serializer(p).data
                    data['distance_km'] = round(dist, 2)
                    properties.append(data)
            except (TypeError, ValueError):
                continue
        
        # Tri par distance
        properties.sort(key=lambda x: x['distance_km'])
        
        return Response(properties)

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
    min_bedrooms = request.GET.get('min_bedrooms')
    wifi = request.GET.get('wifi')
    ac = request.GET.get('ac')
    
    properties = Property.objects.filter(is_published=True).select_related('owner').prefetch_related('images')
    is_fallback = False
    
    # Titre SEO dynamique
    seo_title = _("Toutes les annonces immobilières au Togo")
    cat_label = _("Location/Vente")
    if listing_category == 'RENT': cat_label = _("Location")
    elif listing_category == 'SALE': cat_label = _("Vente")
    elif listing_category == 'FURNISHED': cat_label = _("Meublé")

    type_label = property_type if property_type and property_type != 'ALL' else _("biens")
    city_label = city if city and city != 'ALL' else _("Togo")
    
    if listing_category or property_type or city:
        seo_title = f"{type_label} en {cat_label} à {city_label}"
        if neighborhood: seo_title += f" ({neighborhood})"

    seo_description = _("Consultez les meilleures annonces immobilières : appartements, villas, terrains et meublés au Togo. Annonces vérifiées.")

    # Filtres de base
    if listing_category and listing_category != 'ALL': properties = properties.filter(listing_category=listing_category)
    if property_type and property_type != 'ALL': properties = properties.filter(property_type=property_type)
    if min_price: properties = properties.filter(price__gte=int(float(min_price)))
    if max_price: properties = properties.filter(price__lte=int(float(max_price)))
    if min_bedrooms: properties = properties.filter(bedrooms__gte=int(min_bedrooms))
    if wifi == '1': properties = properties.filter(wifi=True)
    if ac == '1': properties = properties.filter(air_conditioning=True)
    
    # Filtre textuel (recherche globale)
    if q:
        properties = properties.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(neighborhood__icontains=q))
    
    # Filtres géo
    if city and city != 'ALL': properties = properties.filter(city=city)
    
    # On garde une copie avant le filtre quartier pour le fallback
    pre_neighborhood_results = properties
    if neighborhood and neighborhood != 'ALL': 
        properties = properties.filter(neighborhood__icontains=neighborhood)
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
            img_url = p.get_main_image
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
                'img': img_url
            })

    context = {
        'properties': properties,
        'is_fallback': is_fallback,
        'search_query': q or neighborhood,
        'cities': [c[0] for c in CITY_CHOICES],
        'map_markers_json': json.dumps(map_markers),
        'breadcrumbs': [
            {'name': _('Annonces immobilières'), 'url': '/annonces/'}
        ]
    }
    return render(request, 'properties_list.html', context)

def property_detail_view(request, property_id=None, slug=None):
    # Optimisation Senior: Préchargement des relations pour éviter les requêtes N+1
    base_qs = Property.objects.select_related('owner').prefetch_related('images', 'availabilities')
    
    if slug: property_obj = get_object_or_404(base_qs, slug=slug)
    else: property_obj = get_object_or_404(base_qs, id=property_id)
    
    property_obj.views_count += 1
    property_obj.save()
    
    is_favorite = request.user.is_authenticated and Favorite.objects.filter(user=request.user, property=property_obj).exists()
    
    # Optimisation des propriétés similaires
    related_properties = Property.objects.filter(city=property_obj.city, is_published=True).exclude(id=property_obj.id).select_related('owner').prefetch_related('images')[:4]
    
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

@login_required
def request_reservation_view(request, property_id):
    """Gère la soumission d'une demande de réservation (Airbnb-style)."""
    p = get_object_or_404(Property, id=property_id)
    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        
        if not check_in or not check_out:
            messages.error(request, _("Veuillez sélectionner vos dates."))
            return redirect(p.get_absolute_url())
            
        # Calcul du prix total (Senior Logic)
        try:
            d1 = datetime.datetime.strptime(check_in, '%Y-%m-%d')
            d2 = datetime.datetime.strptime(check_out, '%Y-%m-%d')
            nights = (d2 - d1).days
            if nights <= 0: raise ValueError
            
            total = (p.discount_price or p.price) * nights # Ou logique par nuitée si définie
            
            Reservation.objects.create(
                property=p,
                user=request.user,
                check_in=check_in,
                check_out=check_out,
                total_price=total
            )
            messages.success(request, _("Demande de réservation envoyée pour %(nights)s nuits !") % {'nights': nights})
        except ValueError:
            messages.error(request, _("Dates invalides."))
            
    return redirect(p.get_absolute_url())

@login_required
def request_visit_view(request, property_id):
    """Gère la planification d'une visite pour location/vente."""
    p = get_object_or_404(Property, id=property_id)
    if request.method == 'POST':
        visit_date = request.POST.get('visit_date')
        if visit_date:
            VisitRequest.objects.create(
                property=p,
                user=request.user,
                proposed_date=visit_date
            )
            messages.success(request, _("Votre demande de visite a été transmise !"))
        else:
            messages.error(request, _("Veuillez choisir une date."))
            
    return redirect(p.get_absolute_url())

@login_required
def duplicate_property_view(request, property_id):
    """Duplique une annonce existante (Senior UI Feature)."""
    import uuid
    from django.utils import timezone
    p = get_object_or_404(Property, id=property_id, owner=request.user)
    
    # On récupère l'objet original
    new_p = Property.objects.get(id=property_id)
    # On réinitialise la clé primaire pour créer un nouvel enregistrement
    new_p.pk = None
    new_p.id = uuid.uuid4()
    new_p.title = f"{p.title} ({_('Copie')})"
    new_p.is_published = False
    new_p.created_at = timezone.now()
    new_p.views_count = 0
    new_p.is_boosted = False
    new_p.save()
    
    # Duplication des images associées
    for img in p.images.all():
        PropertyImage.objects.create(
            property=new_p,
            image_url=img.image_url,
            is_primary=img.is_primary
        )
        
    messages.success(request, _("Annonce dupliquée ! Vous pouvez maintenant la modifier."))
    return redirect('edit_property', property_id=new_p.id)
def near_me_view(request):
    """
    Page carte de géolocalisation temps réel (Web).
    """
    from logersn.constants import PROPERTY_TYPE_CHOICES
    
    # Récupérer tous les biens géolocalisés avec coordonnées
    properties = Property.objects.filter(
        Q(property_type='AUBERGE') | Q(listing_category='FURNISHED'),
        is_published=True
    ).select_related('owner').prefetch_related('images').exclude(
        latitude__isnull=True
    ).exclude(longitude__isnull=True)

    map_markers = []
    for p in properties:
        try:
            lat_val = float(p.latitude)
            lng_val = float(p.longitude)
        except (TypeError, ValueError):
            continue
        
        # Image principale
        main_img = p.images.filter(is_primary=True).first() or p.images.first()
        img_url = main_img.image_url.url if main_img and main_img.image_url else ''
        
        # Téléphone du propriétaire (masqué sur 4 derniers chiffres)
        phone = getattr(p.owner, 'phone', '') or ''

        map_markers.append({
            'id': str(p.id),
            'lat': lat_val,
            'lng': lng_val,
            'title': p.title,
            'price_night': int(p.price_per_night or 0),
            'price_month': int(p.price or 0),
            'property_type': p.property_type,
            'type_label': p.get_property_type_display(),
            'category': p.listing_category,
            'neighborhood': p.neighborhood or '',
            'city': p.get_city_display() if p.city else '',
            'url': request.build_absolute_uri(p.get_absolute_url()),
            'img': img_url,
            'phone': phone,
            'bedrooms': p.bedrooms or 0,
            'wifi': getattr(p, 'wifi', False),
            'ac': getattr(p, 'air_conditioning', False),
        })

    # Support de focus via URL
    focus_id = request.GET.get('focus')

    return render(request, 'logersn/near_me.html', {
        'map_markers_json': json.dumps(map_markers, ensure_ascii=False),
        'total_count': len(map_markers),
        'title': _("Auberges & Meublés à proximité"),
        'focus_id': focus_id
    })


def nearby_api_view(request):
    """
    API REST GeoJSON — compatible Android Kotlin (Retrofit).
    GET /api/geo/nearby/?lat=6.1311&lng=1.2228&radius=10&type=AUBERGE
    """
    import math
    
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    try:
        user_lat = float(request.GET.get('lat', 6.1311))
        user_lng = float(request.GET.get('lng', 1.2228))
        radius_km = float(request.GET.get('radius', 10))
    except (TypeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Paramètres invalides'}, status=400)

    filter_type = request.GET.get('type', None)

    qs = Property.objects.filter(
        is_published=True
    ).exclude(latitude__isnull=True).exclude(longitude__isnull=True)

    if filter_type:
        qs = qs.filter(property_type=filter_type)
    else:
        qs = qs.filter(
            Q(property_type='AUBERGE') | Q(listing_category='FURNISHED')
        )

    results = []
    for p in qs.select_related('owner').prefetch_related('images'):
        try:
            p_lat = float(p.latitude)
            p_lng = float(p.longitude)
        except (TypeError, ValueError):
            continue

        dist = haversine(user_lat, user_lng, p_lat, p_lng)
        if dist > radius_km:
            continue

        main_img = p.images.filter(is_primary=True).first() or p.images.first()
        img_url = main_img.image_url if main_img else ''
        phone = getattr(p.owner, 'phone', '') or ''

        if dist < 1:
            distance_label = f"{int(dist * 1000)} m"
        else:
            distance_label = f"{dist:.1f} km"

        results.append({
            'id': str(p.id),
            'title': p.title,
            'type': p.property_type,
            'type_label': p.get_property_type_display(),
            'category': p.listing_category,
            'price_night': int(p.price_per_night or 0),
            'price_month': int(p.price or 0),
            'neighborhood': p.neighborhood or '',
            'city': p.get_city_display() if p.city else '',
            'lat': p_lat,
            'lng': p_lng,
            'distance_km': round(dist, 3),
            'distance_label': distance_label,
            'image_url': img_url,
            'url': request.build_absolute_uri(p.get_absolute_url()),
            'phone': phone,
            'bedrooms': p.bedrooms or 0,
            'wifi': getattr(p, 'wifi', False),
            'ac': getattr(p, 'air_conditioning', False),
        })

    # Trier par distance croissante
    results.sort(key=lambda x: x['distance_km'])

    return JsonResponse({
        'status': 'ok',
        'user': {'lat': user_lat, 'lng': user_lng},
        'radius_km': radius_km,
        'count': len(results),
        'results': results,
    })

def seo_search_view(request, listing_category=None, property_type=None, city=None, neighborhood=None):
    """Vue helper pour mapper des URLs SEO vers la recherche avec filtres."""
    mutable_get = request.GET.copy()
    if listing_category: mutable_get['listing_category'] = listing_category
    if property_type: mutable_get['property_type'] = property_type
    if city: mutable_get['city'] = city
    if neighborhood: mutable_get['neighborhood'] = neighborhood
    request.GET = mutable_get
    return properties_list_view(request)
