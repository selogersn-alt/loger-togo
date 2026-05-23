from django.utils.translation import gettext as _
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q, Avg
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse, reverse_lazy
from django.template.loader import render_to_string
from rest_framework import viewsets
from .models import (
    Property, PropertyImage, Favorite, PropertyReview, PropertyAlert, 
    PropertyApplication, MarketingCampaignTemplate, MarketingCampaign,
    VisitRequest, Reservation
)
from .forms import PropertyForm
from .constants import PROPERTY_TYPE_CHOICES, CITY_CHOICES
from .serializers import PropertySerializer, PropertyImageSerializer
import json
import datetime
import math
import uuid
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

class PropertyViewSet(viewsets.ModelViewSet):
    """
    ViewSet API pour les annonces (Utilisé par mobile).
    """
    queryset = Property.objects.filter(is_published=True).order_by('-is_boosted', '-created_at')
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
    # Filtres sécurisés (Évite les erreurs 500 si paramètres vides ou invalides)
    try:
        if min_price and str(min_price).strip(): 
            properties = properties.filter(price__gte=int(float(min_price)))
        if max_price and str(max_price).strip(): 
            properties = properties.filter(price__lte=int(float(max_price)))
        if min_bedrooms and str(min_bedrooms).strip(): 
            properties = properties.filter(bedrooms__gte=int(min_bedrooms))
    except (ValueError, TypeError):
        pass

    if wifi == '1': properties = properties.filter(wifi=True)
    if ac == '1': properties = properties.filter(air_conditioning=True)
    
    # Filtres géo
    if city and city.strip() and city != 'ALL': 
        properties = properties.filter(city=city)
    
    # Filtre textuel (recherche globale)
    if q and q.strip():
        properties = properties.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(neighborhood__icontains=q))
    
    # --- INTELLIGENCE DE RECHERCHE (FALLBACK) ---
    # Si aucun résultat, on propose des annonces similaires (Même ville ou catégorie)
    if properties.count() == 0:
        is_fallback = True
        properties = Property.objects.filter(is_published=True).select_related('owner').prefetch_related('images')
        if city:
            properties = properties.filter(city=city)
        elif listing_category:
            properties = properties.filter(listing_category=listing_category)
        
        properties = properties.order_by('-is_boosted', '-created_at')[:9]

    sort = request.GET.get('sort')
    if not is_fallback:
        if sort == 'price_asc': properties = properties.order_by('-is_boosted', 'price')
        elif sort == 'price_desc': properties = properties.order_by('-is_boosted', '-price')
        else: properties = properties.order_by('-created_at', '-is_boosted')
    
    # --- DONNÉES CARTE ---
    map_markers = []
    for p in properties:
        if p.latitude and p.longitude:
            img_url = p.get_main_image
            # Déterminer le prix à afficher sur la carte et le type
            is_nightly = bool(p.listing_category == 'FURNISHED' and p.price_per_night and p.price_per_night > 0)
            display_price = int(p.price_per_night) if is_nightly else int(p.price) if p.price else 0
            
            map_markers.append({
                'id': str(p.id),
                'lat': float(p.latitude) if p.latitude else 0,
                'lng': float(p.longitude) if p.longitude else 0,
                'title': p.title or "",
                'price': display_price,
                'is_nightly': is_nightly,
                'category': p.listing_category,
                'type': p.get_property_type_display(),
                'document_type': p.get_document_type_display() if p.listing_category == 'SALE' else '',
                'neighborhood': p.neighborhood or "",
                'city': p.city or "",
                'url': p.get_absolute_url(),
                'image': img_url or ""
            })

    context = {
        'properties': properties,
        'is_fallback': is_fallback,
        'search_query': q or neighborhood,
        'cities': [c[0] for c in CITY_CHOICES],
        'property_types': PROPERTY_TYPE_CHOICES,
        'listing_categories': Property.CategoryEnum.choices,
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
        messages.error(request, _("Accès professionnel requis pour publier une annonce."))
        return redirect('dashboard')

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Évite les doubles soumissions par clic rapide
                p = form.save(commit=False)
                p.owner = request.user
                p.save()
                
                # Gestion robuste des images (Support AJAX & Multi-part)
                # On récupère les images soit du formulaire nettoyé, soit directement des FILES
                images = request.FILES.getlist('images')
                
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Sauvegarde de {len(images)} images pour le bien {p.id}")

                for i, img in enumerate(images):
                    PropertyImage.objects.create(property=p, image_url=img, is_primary=(i == 0))
                
                # Si c'est une requête AJAX, on répond en JSON
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success', 'id': str(p.id), 'redirect': f'/annonces/{p.id}/'})

                messages.success(request, _("Votre annonce a été créée avec succès !"))
                return redirect('initiate_payment', property_id=p.id, payment_type='PUBLICATION')
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Erreur création property: {e}")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
                messages.error(request, _("Erreur lors de la création : %s") % str(e))
    else: 
        form = PropertyForm()
    
    return render(request, 'property_form.html', {
        'form': form, 
        'togo_neighborhoods': TOGO_NEIGHBORHOODS
    })

@login_required
def edit_property_view(request, property_id):
    p = get_object_or_404(Property, id=property_id, owner=request.user)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=p)
        if form.is_valid():
            p = form.save()
            
            # Gestion robuste des images en édition
            new_images = request.FILES.getlist('images')
            if new_images:
                import logging
                logging.getLogger(__name__).info(f"Ajout de {len(new_images)} nouvelles images pour {p.id}")
                for img in new_images:
                    PropertyImage.objects.create(property=p, image_url=img)
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'id': str(p.id), 'redirect': f'/annonces/{p.id}/'})

            messages.success(request, _("Annonce mise à jour avec succès !"))
            return redirect('/mon-compte/?section=ads')
    else:
        form = PropertyForm(instance=p)
    
    return render(request, 'property_form.html', {
        'form': form, 
        'is_edit': True, 
        'property': p, 
        'togo_neighborhoods': TOGO_NEIGHBORHOODS
    })

@login_required
def delete_property_view(request, property_id):
    p = get_object_or_404(Property, id=property_id, owner=request.user)
    if request.method == 'POST': p.delete(); return redirect('/mon-compte/?section=ads')
    return render(request, 'confirm_delete.html', {'property': p, 'type': 'annonce'})

@login_required
def delete_image_view(request, image_id):
    img = get_object_or_404(PropertyImage, id=image_id, property__owner=request.user)
    property_id = img.property.id
    img.delete()
    messages.success(request, _("Image supprimée."))
    return redirect('edit_property', property_id=property_id)

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
    from logertogo.emails import send_visit_request_email
    import logging
    logger = logging.getLogger('django')
    
    p = get_object_or_404(Property, id=property_id)
    if request.method == 'POST':
        visit_date_str = request.POST.get('visit_date')
        if visit_date_str:
            try:
                # Parsing robuste de la date (format datetime-local)
                proposed_date = parse_datetime(visit_date_str)
                if not proposed_date:
                    # Fallback si format inattendu
                    from django.utils.dateparse import parse_date
                    proposed_date = parse_datetime(visit_date_str.replace('T', ' '))
                
                if proposed_date:
                    # Rendre la date aware si elle est naive pour éviter l'erreur 500 (comparison offset-naive vs offset-aware)
                    if timezone.is_naive(proposed_date):
                        proposed_date = timezone.make_aware(proposed_date)

                    # Vérifier si la date est dans le futur
                    if proposed_date < timezone.now():
                        messages.error(request, _("La date de visite doit être dans le futur."))
                        return redirect(p.get_absolute_url())

                    visit = VisitRequest.objects.create(
                        property=p,
                        user=request.user,
                        proposed_date=proposed_date
                    )
                    
                    # Notification email au propriétaire
                    if p.owner.email:
                        try:
                            send_visit_request_email(p.owner, request.user, p, proposed_date)
                        except Exception as e:
                            logger.error(f"Failed to send visit request email: {e}")

                    messages.success(request, _("Votre demande de visite a été transmise !"))
                    return redirect('visit_success', visit_id=visit.id)
                else:
                    messages.error(request, _("Format de date invalide."))
            except Exception as e:
                logger.error(f"Error creating VisitRequest: {e}")
                messages.error(request, _("Une erreur est survenue lors de l'enregistrement de votre demande."))
        else:
            messages.error(request, _("Veuillez choisir une date."))
            
    return redirect(p.get_absolute_url())

@login_required
def visit_success_view(request, visit_id):
    """Page de confirmation de succès pour une demande de visite."""
    visit = get_object_or_404(VisitRequest, id=visit_id, user=request.user)
    return render(request, 'logersn/visit_success.html', {'visit': visit})

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
    new_p.slug = None
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
    
    # Récupérer uniquement les hôtels et auberges géolocalisés avec coordonnées
    properties = Property.objects.filter(
        is_published=True,
        property_type__in=['HOTEL', 'AUBERGE']
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

        # Déterminer le prix et s'il s'agit d'un prix par nuitée
        price_night = int(p.price_per_night or 0)
        price_month = int(p.price or 0)
        is_nightly = bool(p.listing_category == 'FURNISHED' and price_night > 0)

        map_markers.append({
            'id': str(p.id),
            'lat': lat_val,
            'lng': lng_val,
            'title': p.title,
            'price_night': price_night,
            'price_month': price_month,
            'is_nightly': is_nightly,
            'property_type': p.property_type,
            'type_label': p.get_property_type_display(),
            'category': p.listing_category,
            'neighborhood': p.neighborhood or '',
            'city': p.get_city_display() if p.city else '',
            'url': request.build_absolute_uri(p.get_absolute_url()),
            'image': img_url,
            'phone': phone,
            'bedrooms': p.bedrooms or 0,
            'wifi': getattr(p, 'wifi', False),
            'ac': getattr(p, 'air_conditioning', False),
        })

    # Support de focus via URL
    focus_id = request.GET.get('focus')

    return render(request, 'logersn/near_me.html', {
        'properties_json': json.dumps(map_markers, ensure_ascii=False),
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





@staff_member_required
def admin_select_email_template(request):
    user_ids = request.session.get('selected_users_for_email', [])
    
    # Prise en charge d'un ID unique via URL (pour le bouton direct dans l'admin)
    single_user_id = request.GET.get('user_id')
    if single_user_id and single_user_id not in user_ids:
        user_ids = [single_user_id]
        
    if not user_ids:
        messages.error(request, "Aucun utilisateur sélectionné.")
        return HttpResponseRedirect('/admin/users/user/')
    
    from users.models import User
    users = User.objects.filter(id__in=user_ids)
    templates = MarketingCampaignTemplate.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action') # 'send' or 'preview'
        template_id = request.POST.get('template_id')
        custom_subject = request.POST.get('subject')
        custom_content = request.POST.get('content')
        scheduled_for = request.POST.get('scheduled_for')
        
        template = None
        if template_id:
            template = get_object_or_404(MarketingCampaignTemplate, id=template_id)

        # Remplacement de tags pour la prévisualisation (premier utilisateur)
        preview_user = users.first()
        preview_content = custom_content or (template.content if template else "")
        if preview_user:
            preview_content = preview_content.replace('[PRENOM]', preview_user.first_name or "Client")
            preview_content = preview_content.replace('[NOM]', preview_user.last_name or "")

        if action == 'preview':
            # Rendu du template mail réel pour l'aperçu
            full_html = render_to_string('emails/base_email.html', {
                'content': preview_content,
                'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://logertogo.com'
            })
            return render(request, 'admin/email_preview.html', {'html_content': full_html})

        elif action == 'send':
            # Création de la campagne en base
            campaign = MarketingCampaign.objects.create(
                template=template,
                subject=custom_subject or (template.subject if template else "Sans sujet"),
                content=custom_content or (template.content if template else ""),
                scheduled_for=scheduled_for if scheduled_for else None
            )
            campaign.individual_recipients.set(users)
            
            # Si pas de date, on envoie tout de suite
            if not scheduled_for:
                count = 0
                for user in users:
                    if user.email:
                        user_content = campaign.content.replace('[PRENOM]', user.first_name or "").replace('[NOM]', user.last_name or "")
                        email = EmailMultiAlternatives(
                            subject=campaign.subject,
                            body="HTML client needed",
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[user.email]
                        )
                        email.attach_alternative(render_to_string('emails/base_email.html', {'content': user_content}), "text/html")
                        email.send()
                        count += 1
                campaign.is_sent = True
                campaign.sent_at = timezone.now()
                campaign.save()
                messages.success(request, f"Succès : {count} emails envoyés immédiatement.")
            else:
                messages.success(request, f"Campagne planifiée pour le {scheduled_for}.")
            
            if 'selected_users_for_email' in request.session:
                del request.session['selected_users_for_email']
            return HttpResponseRedirect('/admin/users/user/')

    return render(request, 'admin/select_email_template.html', {
        'templates': templates,
        'users': users,
        'user_count': users.count(),
        'title': "Configurer la campagne"
    })

@staff_member_required
def get_campaign_template_view(request, template_id):
    template = get_object_or_404(MarketingCampaignTemplate, id=template_id)
    return JsonResponse({
        'subject': template.subject,
        'content': template.content
    })
