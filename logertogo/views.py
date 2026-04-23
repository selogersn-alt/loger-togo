from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.db.models import Sum, Count, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
import datetime
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.cache import cache_page

from logersn.models import Property, Favorite
from logersn.forms import PropertyForm
from users.models import User, SearchLog
from chat.models import Conversation, Message

# Import sécurisé de django-countries
try:
    from django_countries import countries as COUNTRY_CHOICES
except ImportError:
    COUNTRY_CHOICES = []

# @cache_page(60 * 15)
def home_view(request):
    """
    Vue principale : Moteur de recherche d'annonces immobilières au Togo.
    """
    from logersn.constants import CITY_CHOICES, PROPERTY_TYPE_CHOICES
    from django.core.paginator import Paginator

    # Recherche de biens
    city = request.GET.get('city')
    property_type = request.GET.get('property_type')
    query = request.GET.get('query', '')

    # Base Queryset
    try:
        all_properties = Property.objects.filter(is_published=True).select_related('owner').prefetch_related('images')
        
        if city and city != 'ALL':
            all_properties = all_properties.filter(city=city)
        if property_type and property_type != 'ALL':
            all_properties = all_properties.filter(property_type=property_type)
        if query:
            all_properties = all_properties.filter(
                Q(title__icontains=query) | Q(description__icontains=query) | Q(neighborhood__icontains=query)
            )

        all_properties = all_properties.order_by('-created_at')

        # Slider : Uniquement les annonces boostées
        boosted_properties = Property.objects.filter(
            is_boosted=True,
            is_published=True
        ).select_related('owner').prefetch_related('images').order_by('-created_at')[:10]

        paginator = Paginator(all_properties, 12)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.page(page_number)
    except Exception:
        boosted_properties = Property.objects.none()
        page_obj = None

    # Professionnels à la Une
    try:
        featured_pros = User.objects.filter(is_verified_pro=True).exclude(role='TENANT').order_by('?')[:30]
    except Exception:
        featured_pros = []

    return render(request, 'home.html', {
        'page_obj': page_obj,
        'boosted_properties': boosted_properties,
        'featured_pros': featured_pros,
        'cities': CITY_CHOICES,
        'property_types': PROPERTY_TYPE_CHOICES,
        'neighborhoods': [],
        'query': query
    })

def about_view(request):
    return render(request, 'about.html')

def verified_professionals_view(request):
    # Les pros vérifiés par l'admin (badge is_verified_pro=True) et qui sont Agency, Broker, Agent, Landlord
    try:
        pros = User.objects.filter(is_verified_pro=True).exclude(role='TENANT').order_by('role', 'company_name', 'phone_number')
    except Exception:
        pros = User.objects.none()
    
    context = {
        'professionals': pros
    }
    return render(request, 'professionals_list.html', context)

def properties_list_view(request):
    # Récupérer les paramètres de recherche
    city = request.GET.get('city')
    neighborhood = request.GET.get('neighborhood')
    property_type = request.GET.get('property_type')
    listing_category = request.GET.get('listing_category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    owner_id = request.GET.get('owner')
    
    # Base Queryset optimisé avec prefetch_related et select_related (Analytics N+1 fixes)
    try:
        properties = Property.objects.filter(is_published=True).select_related('owner').prefetch_related('images')
    except Exception:
        properties = Property.objects.none()
    
    # Filtrage par propriétaire
    if owner_id:
        properties = properties.filter(owner_id=owner_id)
        
    # Filtrage
    if listing_category and listing_category != 'ALL':
        properties = properties.filter(listing_category=listing_category)
    if city and city != 'ALL':
        properties = properties.filter(city=city)
    if neighborhood and neighborhood != 'ALL':
        properties = properties.filter(neighborhood=neighborhood)
    if property_type and property_type != 'ALL':
        properties = properties.filter(property_type=property_type)
    if min_price:
        properties = properties.filter(price__gte=min_price)
    if max_price:
        properties = properties.filter(price__lte=max_price)
        
    # Filtrage Amenities
    if request.GET.get('wifi') == 'on':
        properties = properties.filter(wifi=True)
    if request.GET.get('swimming_pool') == 'on':
        properties = properties.filter(swimming_pool=True)
    if request.GET.get('air_conditioning') == 'on':
        properties = properties.filter(air_conditioning=True)
    if request.GET.get('has_garage') == 'on':
        properties = properties.filter(has_garage=True)
    if request.GET.get('generator') == 'on':
        properties = properties.filter(generator=True)
        
    # Tris : Boosté en premier, puis le tri choisi par l'utilisateur
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        properties = properties.order_by('-is_boosted', 'price')
    elif sort == 'price_desc':
        properties = properties.order_by('-is_boosted', '-price')
    else:
        properties = properties.order_by('-created_at', '-id')
        
    # Extraire les annonces pour le bandeau défilant du haut (Boostées uniquement)
    try:
        boosted_slider = Property.objects.filter(is_published=True, is_boosted=True).order_by('-created_at', '-id')[:10]
    except Exception:
        boosted_slider = Property.objects.none()
    
    from logersn.constants import CITY_CHOICES, PROPERTY_TYPE_CHOICES
    
    # Génération dynamique de la description SEO (Phase 4)
    seo_market_description = ""
    if city and city != 'ALL':
        city_name = dict(CITY_CHOICES).get(city, city)
        seo_market_description = f"Le marché immobilier à {city_name} offre de nombreuses opportunités. Que vous cherchiez un appartement moderne, une villa de standing ou une maison familiale, Loger Togo vous accompagne pour sécuriser votre transaction immobilière au Togo."
    else:
        seo_market_description = "Loger Togo est la plateforme de référence pour l'immobilier au Togo. Nous connectons bailleurs, agences et locataires dans un environnement sécurisé. Retrouvez nos annonces d'appartements, de villas et de terrains à Lomé, Kara, Kpalimé et partout au Togo."

    # Génération dynamique des métadonnées SEO (SEO Local Power)
    seo_title = "Annonces Immobilières au Togo"
    seo_description = "Retrouvez les meilleures annonces d'appartements, villas et terrains au Togo sur Loger Togo."
    
    type_label = dict(PROPERTY_TYPE_CHOICES).get(property_type, "Biens immobiliers") if property_type and property_type != 'ALL' else "Biens immobiliers"
    cat_label = "à vendre" if listing_category == 'SALE' else "meublés" if listing_category == 'FURNISHED' else "en location"
    
    if neighborhood and neighborhood != 'ALL':
        n_name = neighborhood
        seo_title = f"{type_label} {cat_label} à {n_name}, {dict(CITY_CHOICES).get(city, city)}"
        seo_description = f"Découvrez notre sélection de {type_label.lower()} {cat_label} située à {n_name}. Loger Togo facilite votre recherche immobilière au Togo."
    elif city and city != 'ALL':
        c_name = dict(CITY_CHOICES).get(city, city)
        seo_title = f"{type_label} {cat_label} à {c_name} | Meilleures offres immo"
        seo_description = f"Trouvez votre futur {type_label.lower()} {cat_label} à {c_name}. Loger Togo : la plateforme de confiance pour l'immobilier au Togo."
    elif property_type and property_type != 'ALL':
        seo_title = f"{type_label} {cat_label} au Togo | Loger Togo"

    # Données carte Leaflet (uniquement les biens avec coordonnées)
    import json
    map_markers = []
    for p in properties:
        if p.latitude and p.longitude:
            first_img = p.images.first()
            map_markers.append({
                'id': str(p.id),
                'lat': float(p.latitude),
                'lng': float(p.longitude),
                'title': p.title,
                'price': int(p.price),
                'city': p.city,
                'neighborhood': p.neighborhood,
                'type': p.get_property_type_display(),
                'url': p.get_absolute_url(),
                'img': first_img.image_url.url if first_img else '',
                'category': p.listing_category,
            })

    context = {
        'properties': properties,
        'boosted_slider': boosted_slider,
        'cities': CITY_CHOICES,
        'neighborhoods': [],
        'property_types': PROPERTY_TYPE_CHOICES,
        'current_filters': request.GET,
        'seo_title': seo_title,
        'seo_description': seo_description,
        'seo_market_description': seo_market_description,
        'map_markers_json': json.dumps(map_markers),
    }

    return render(request, 'properties_list.html', context)

def property_detail_view(request, property_id=None, slug=None):
    # Récupère l'annonce par son Slug (SEO) ou son ID unique (Compatibilité)
    if slug:
        property_obj = get_object_or_404(Property, slug=slug)
    else:
        property_obj = get_object_or_404(Property, id=property_id)
    
    # Sécurité : Si l'annonce n'est pas publiée, SEUL l'admin ou le propriétaire peut la voir
    if not property_obj.is_published:
        if not (request.user.is_authenticated and (request.user == property_obj.owner or request.user.is_staff)):
            from django.http import Http404
            raise Http404("Cette annonce est en attente de validation par l'administrateur.")
    
    # Incrémentation des statistiques de vue (Analytics)
    property_obj.views_count += 1
    property_obj.save()
    
    # Biens similaires (même ville ou même type)
    related_properties = Property.objects.filter(
        is_published=True
    ).filter(
        models.Q(city=property_obj.city) | models.Q(property_type=property_obj.property_type)
    ).exclude(id=property_obj.id)[:4]
    
    from logersn.models import PropertyReview
    from django.db.models import Avg
    approved_reviews = PropertyReview.objects.filter(property=property_obj, is_approved=True)
    avg_rating = approved_reviews.aggregate(avg=Avg('rating'))['avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)
    user_has_reviewed = (
        request.user.is_authenticated and
        PropertyReview.objects.filter(property=property_obj, reviewer=request.user).exists()
    )

    context = {
        'property': property_obj,
        'related_properties': related_properties,
        'approved_reviews': approved_reviews,
        'avg_rating': avg_rating,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'property_detail.html', context)

def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        user = authenticate(request, phone_number=phone, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenue, {user.phone_number} !")
            return redirect('dashboard')
        else:
            messages.error(request, "Numéro de téléphone ou mot de passe incorrect.")
            
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        no_email = request.POST.get('no_email')
        role = request.POST.get('role', 'TENANT')
        company_name = request.POST.get('company_name')
        coverage_area = request.POST.get('coverage_area')
        
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'register.html')
            
        if not no_email and not email:
            messages.error(request, "Veuillez fournir un email ou cocher la case 'Je n'ai pas d'adresse email'.")
            return render(request, 'register.html')
            
        if email and User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'register.html')
            
        if User.objects.filter(phone_number=phone).exists():
            messages.error(request, "Ce numéro de téléphone est déjà utilisé.")
            return render(request, 'register.html')
            
        # Création de l'utilisateur
        user = User.objects.create_user(phone_number=phone, email=email if email else None, password=password, role=role)
        user.company_name = company_name
        user.coverage_area = coverage_area
        user.save()
        
        login(request, user)
        # Email de bienvenue
        if user.email:
            try:
                from logertogo.emails import send_account_created_email
                send_account_created_email(user)
            except Exception:
                pass
        messages.success(request, "Votre compte a été créé avec succès !")
        return redirect('dashboard')
        
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('home')

@login_required
def dashboard_view(request):
    import datetime
    from django.db.models import Count, Sum
    from django.http import HttpResponse
    import csv

    # --- DATE FILTER ---
    date_from_str = request.GET.get('date_from')
    date_to_str   = request.GET.get('date_to')
    date_from = None
    date_to   = None
    try:
        if date_from_str:
            date_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
        if date_to_str:
            date_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()
    except ValueError:
        pass

    # --- EXPORT CSV ---
    export = request.GET.get('export')
    
    # --- CONVERSATIONS ---
    conversations = request.user.conversations.prefetch_related('messages').all()
    if request.user.is_staff:
        from chat.models import Conversation
        support_convs = Conversation.objects.filter(topic=Conversation.TopicEnum.SUPPORT).prefetch_related('messages')
        conversations = (conversations | support_convs).distinct().order_by('-updated_at')

    active_conv_id = request.GET.get('conv')
    active_conversation = None
    if active_conv_id:
        active_conversation = conversations.filter(id=active_conv_id).first()
    elif conversations.exists():
        active_conversation = conversations.first()

    # --- PROPERTIES ---
    properties = request.user.properties.all().order_by('-created_at')
    if date_from:
        properties = properties.filter(created_at__date__gte=date_from)
    if date_to:
        properties = properties.filter(created_at__date__lte=date_to)

    # Filter by city / type for pros
    filter_city = request.GET.get('filter_city', '')
    filter_type = request.GET.get('filter_type', '')
    filter_status = request.GET.get('filter_status', '')
    if filter_city:
        properties = properties.filter(city=filter_city)
    if filter_type:
        properties = properties.filter(property_type=filter_type)
    if filter_status == 'published':
        properties = properties.filter(is_published=True)
    elif filter_status == 'pending':
        properties = properties.filter(is_published=False)

    approved_count = request.user.properties.filter(is_published=True).count()
    pending_count  = request.user.properties.filter(is_published=False).count()

    # --- APPLICATIONS (not yet implemented as a separate model) ---
    received_applications = []
    app_filter = ''

    # --- TRANSACTIONS / STATS ---
    try:
        from logersn.models import Transaction
        my_transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
        if date_from:
            my_transactions = my_transactions.filter(created_at__date__gte=date_from)
        if date_to:
            my_transactions = my_transactions.filter(created_at__date__lte=date_to)
        total_spent = my_transactions.filter(status='SUCCESS').aggregate(t=Sum('amount'))['t'] or 0
        views_total = request.user.properties.aggregate(v=Sum('views_count'))['v'] or 0
    except Exception:
        my_transactions = []
        total_spent = 0
        views_total = 0

    # --- CSV EXPORT ---
    if export == 'properties':
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="mes_annonces.csv"'
        w = csv.writer(response)
        w.writerow(['Titre', 'Ville', 'Type', 'Prix (FCFA)', 'Vues', 'Publiée', 'Date'])
        for p in properties:
            w.writerow([p.title, p.city, p.get_property_type_display(), p.price, p.views_count, 'Oui' if p.is_published else 'Non', p.created_at.strftime('%d/%m/%Y')])
        return response
    if export == 'transactions':
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="mes_transactions.csv"'
        w = csv.writer(response)
        w.writerow(['Référence', 'Type', 'Montant (FCFA)', 'Statut', 'Date'])
        for t in my_transactions:
            w.writerow([t.reference, t.get_transaction_type_display(), t.amount, t.status, t.created_at.strftime('%d/%m/%Y')])
        return response

    from logersn.constants import CITY_CHOICES, PROPERTY_TYPE_CHOICES

    context = {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'properties': properties,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'received_applications': received_applications,
        'my_transactions': my_transactions,
        'total_spent': total_spent,
        'views_total': views_total,
        # filters
        'date_from': date_from_str or '',
        'date_to': date_to_str or '',
        'filter_city': filter_city,
        'filter_type': filter_type,
        'filter_status': filter_status,
        'app_filter': app_filter if received_applications is not None else '',
        'cities': CITY_CHOICES,
        'property_types': PROPERTY_TYPE_CHOICES,
    }
    return render(request, 'dashboard.html', context)


from logersn.utils import FedaPayBridge
from logersn.models import Property, PropertyImage, Transaction
from logersn.forms import PropertyForm

@login_required
def create_property_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.is_published = False 
            property_obj.is_paid = False
            property_obj.save()
            
            # Gestion des images multiples
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                PropertyImage.objects.create(
                    property=property_obj,
                    image_url=image,
                    is_primary=(i == 0)
                )
                
            pricing = FedaPayBridge.get_pricing()
            fee = pricing['publication_rent']
            if property_obj.listing_category == 'SALE': fee = pricing['publication_sale']
            elif property_obj.listing_category == 'FURNISHED': fee = pricing['publication_furnished']
            
            messages.info(request, f"Annonce enregistrée ! Veuillez procéder au paiement des frais de publication ({int(fee)}F) pour l'activer.")
            return redirect('initiate_payment', property_id=property_obj.id, payment_type='PUBLICATION')
    else:
        form = PropertyForm()
    
    return render(request, 'property_form.html', {'form': form})

@login_required
def initiate_payment_view(request, property_id, payment_type):
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)
    days = int(request.GET.get('days', 1)) 
    
    transaction = FedaPayBridge.initiate_transaction(request.user, payment_type, property_obj, days)
    
    # Gestion de la promotion "TOUT GRATUIT" (Démo/Promo Admin)
    if transaction.amount <= 0:
        # On simule un succès immédiat si c'est gratuit
        return redirect(f"/payments/callback/?ref={transaction.reference}&status=success")
        
    payment_url = FedaPayBridge.generate_payment_url(transaction)
    return redirect(payment_url)

@login_required
def checkout_payment_view(request, property_id, payment_type):
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)
    pricing = FedaPayBridge.get_pricing()
    
    # Récupération du prix unitaire selon le type
    unit_price = 0
    if payment_type == 'PUBLICATION':
        cat = property_obj.listing_category
        if cat == 'RENT': unit_price = pricing['publication_rent']
        elif cat == 'SALE': unit_price = pricing['publication_sale']
        elif cat == 'FURNISHED': unit_price = pricing['publication_furnished']
        else: unit_price = pricing['publication_rent']
    elif payment_type == 'BOOST': unit_price = pricing['boost']
    elif payment_type == 'POPUP': unit_price = pricing['popup']
    
    context = {
        'property': property_obj,
        'payment_type': payment_type,
        'unit_price': unit_price,
        'config': pricing
    }
    return render(request, 'checkout.html', context)

def payment_callback_view(request):
    ref = request.GET.get('ref')
    status = request.GET.get('status')
    
    transaction = get_object_or_404(Transaction, reference=ref)
    
    if status == 'success':
        transaction.status = 'SUCCESS'
        transaction.save()
        
        # Activation selon le type
        if transaction.transaction_type == 'PUBLICATION' and transaction.property:
            transaction.property.is_paid = True
            transaction.property.save()
            messages.success(request, "Paiement réussi ! Votre annonce est maintenant prête à être validée par l'admin.")
            
        elif transaction.transaction_type == 'BOOST' and transaction.property:
            transaction.property.is_boosted = True
            # Activation pour la durée payée
            transaction.property.boost_until = timezone.now() + datetime.timedelta(days=transaction.days)
            transaction.property.save()
            messages.success(request, f"Félicitations ! Votre annonce est maintenant boostée pour {transaction.days} jour(s).")
            
        elif transaction.transaction_type == 'POPUP' and transaction.property:
            transaction.property.is_featured_popup = True
            # Activation pour la durée payée
            transaction.property.popup_until = timezone.now() + datetime.timedelta(days=transaction.days)
            transaction.property.save()
            messages.success(request, f"Félicitations ! Votre annonce apparaîtra désormais dans les pop-ups pour {transaction.days} jour(s).")
            
        return redirect('payment_success', transaction_id=transaction.id)
    
    messages.error(request, "Le paiement n'a pas pu aboutir.")
    return redirect('dashboard')

@login_required
def payment_success_view(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    return render(request, 'payment_success.html', {'transaction': transaction})

def password_recovery_view(request):
    phone = request.GET.get('phone', '').strip()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and phone:
        from users.models import User
        user = User.objects.filter(phone_number__icontains=phone).first()
        if user:
            return JsonResponse({
                'exists': True, 
                'has_email': bool(user.email),
                'email_masked': (user.email[:3] + '****' + user.email[user.email.find('@'):]) if user.email else ''
            })
        return JsonResponse({'exists': False})

    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        method = request.POST.get('method', 'whatsapp') 
        
        from users.models import User
        user = User.objects.filter(phone_number__icontains=phone).first()
        
        if user:
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes
            from django.contrib.auth.tokens import default_token_generator
            from .emails import send_password_reset_email
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm_public', kwargs={'uidb64': uid, 'token': token})
            )

            if method == 'email' and user.email:
                send_password_reset_email(user, reset_url)
                messages.success(request, f"Un lien de réinitialisation sécurisé a été envoyé à l'adresse {user.email}")
                return redirect('login')
            else:
                # On prépare pour le template
                return render(request, 'recovery.html', {'phone': phone, 'show_wa_link': True, 'reset_url': reset_url})
        else:
            messages.error(request, "Numéro de téléphone inconnu.")
            
    return render(request, 'recovery.html')

def password_reset_confirm_view(request, uidb64, token):
    """Interface Frontend pour définir un nouveau mot de passe."""
    from users.models import User
    from django.utils.encoding import force_str
    from django.utils.http import urlsafe_base64_decode
    from django.contrib.auth.tokens import default_token_generator
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, Exception):
        messages.error(request, "Lien de réinitialisation invalide.")
        return redirect('password_recovery')

    if default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password and new_password == confirm_password:
                user.set_password(new_password)
                user.is_phone_verified = True
                user.save()
                messages.success(request, "Mot de passe réinitialisé ! Vous pouvez vous connecter.")
                return redirect('login')
            else:
                messages.error(request, "Les mots de passe ne correspondent pas.")
        
        return render(request, 'password_reset_confirm_public.html', {
            'uidb64': uidb64, 
            'token': token,
            'reset_user': user
        })
    else:
        messages.error(request, "Lien de réinitialisation expiré ou déjà utilisé.")
        return redirect('password_recovery')

@login_required
def admin_generate_reset_link(request, user_id):
    """Génère un lien de réinitialisation. Option email=1 pour envoi direct."""
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes
    from django.contrib.auth.tokens import default_token_generator
    from .emails import send_password_reset_email
    
    if not request.user.is_staff:
        return JsonResponse({'error': 'Accès interdit'}, status=403)
        
    from users.models import User
    user = get_object_or_404(User, pk=user_id)
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Construire l'URL absolue (en utilisant le nom public pour les utilisateurs)
    reset_url = request.build_absolute_uri(
        reverse('password_reset_confirm_public', kwargs={'uidb64': uid, 'token': token})
    )
    
    # Option Envoi Direct par Email
    if request.GET.get('email') == '1' and user.email:
        send_password_reset_email(user, reset_url)
        messages.success(request, f"Lien de réinitialisation envoyé par e-mail à {user.email}")
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

    return JsonResponse({'reset_url': reset_url, 'phone': user.phone_number})

@login_required
def edit_property_view(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            property_obj = form.save(commit=False)
            # On repasse en attente de validation si modif importante (optionnel)
            property_obj.is_published = False 
            property_obj.save()
            
            # Ajout de nouvelles images si fournies
            images = request.FILES.getlist('images')
            if images:
                for image in images:
                    PropertyImage.objects.create(
                        property=property_obj,
                        image_url=image
                    )
            
            messages.success(request, "Votre annonce a été mise à jour ! Elle sera de nouveau visible après validation.")
            return redirect('dashboard')
    else:
        form = PropertyForm(instance=property_obj)
    
    return render(request, 'property_form.html', {'form': form, 'is_edit': True, 'property': property_obj})

@login_required
def delete_property_view(request, property_id):
    from logersn.models import Property
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)
    
    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, "L'annonce a été supprimée définitivement.")
        return redirect('dashboard')
    
    return render(request, 'confirm_delete.html', {'property': property_obj, 'type': 'annonce'})

@login_required
def initiate_chat_view(request, property_id):
    """Start or resume a conversation with a property owner."""
    from logersn.models import Property
    from chat.models import Conversation
    
    target_property = get_object_or_404(Property, id=property_id)
    
    # Incrémentation des statistiques d'interaction (Analytics)
    target_property.clicks_count += 1
    target_property.save()
    
    owner = target_property.owner
    
    if owner == request.user:
        messages.info(request, "C'est votre propre annonce ! Consultez vos messages reçus dans le tableau de bord.")
        return redirect('dashboard')
        
    # Check for existing conversation for this property between these two users
    conversation = Conversation.objects.filter(
        topic=Conversation.TopicEnum.PROPERTY_INQUIRY,
        related_property=target_property,
        participants=request.user
    ).filter(participants=owner).first()
    
    if not conversation:
        conversation = Conversation.objects.create(
            topic=Conversation.TopicEnum.PROPERTY_INQUIRY,
            related_property=target_property
        )
        conversation.participants.add(request.user, owner)
        
    return redirect(f"{reverse('dashboard')}?conv={conversation.id}")

@login_required
def start_support_view(request):
    """Start or resume a conversation with Customer Support (Admin)."""
    from chat.models import Conversation
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        messages.error(request, "Le service client est momentanément indisponible.")
        return redirect('dashboard')
        
    conversation = Conversation.objects.filter(
        topic=Conversation.TopicEnum.SUPPORT,
        participants=request.user
    ).filter(participants=admin_user).first()
    
    if not conversation:
        conversation = Conversation.objects.create(topic=Conversation.TopicEnum.SUPPORT)
        conversation.participants.add(request.user, admin_user)
        
    return redirect(f"{reverse('dashboard')}?conv={conversation.id}")

@login_required
def send_message_view(request, conversation_id=None):
    if request.method == 'POST':
        content = request.POST.get('content')
        if not content:
            return redirect('dashboard')
            
        if conversation_id:
            # S'assurer que l'utilisateur fait bien partie de la conversation
            conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
        else:
            # Create a new default Support conversation if none exists
            admin_user = User.objects.filter(is_superuser=True).first()
            conversation = Conversation.objects.create(topic=Conversation.TopicEnum.SUPPORT)
            conversation.participants.add(request.user)
            if admin_user:
                conversation.participants.add(admin_user)
                
        # Créer le message en base de données
        new_msg = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Notifier les autres participants par email (hors l'expéditeur)
        try:
            from logertogo.emails import send_new_message_notification
            for participant in conversation.participants.exclude(id=request.user.id):
                if participant.email:
                    send_new_message_notification(
                        recipient=participant,
                        sender=request.user,
                        conversation=conversation,
                        message_preview=content[:120]
                    )
        except Exception:
            pass

        # Support AJAX : Si l'envoi est fait via script, on répond en JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == 'true':
            from django.http import JsonResponse
            return JsonResponse({
                'status': 'success',
                'message_id': str(new_msg.id),
                'content': new_msg.content,
                'created_at': new_msg.created_at.strftime('%H:%M'),
                'sender_name': "Support Logertogo" if request.user.is_staff else request.user.email or request.user.phone_number
            })
            
        return redirect(f"/mon-compte/?conv={conversation.id}#chat")
    
    return redirect('dashboard')

@login_required
def kyc_submit_view(request):
    from users.forms import KYCProfileForm
    
    if hasattr(request.user, 'kyc_profile'):
        messages.info(request, "Vous avez déjà soumis votre dossier KYC.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = KYCProfileForm(request.POST, request.FILES)
        if form.is_valid():
            kyc = form.save(commit=False)
            kyc.user = request.user
            kyc.save()
            messages.success(request, "Votre dossier d'identité a bien été transmis. Nous allons le vérifier.")
            return redirect('dashboard')
    else:
        form = KYCProfileForm()
        
    return render(request, 'kyc_submit.html', {'form': form})

@login_required
def nils_search_view(request):
    from django.db.models import Sum, Q
    from solvable.models import IncidentReport
    from users.models import NILS_Profile, SearchLog
    from logersn.constants import COUNTRY_CHOICES

    # SECURITY: Only allowed for Pros!
    if request.user.role == 'TENANT' and not request.user.is_staff:
        messages.error(request, "Accès réservé aux bailleurs et agences professionnels.")
        return redirect('dashboard')

    # Multi-critères ou Recherche Unique (Mobile/Home)
    name_q = request.GET.get('name_query', '').strip()
    phone_q = request.GET.get('phone_query', '').strip()
    doc_q = request.GET.get('doc_query', '').strip()
    country_q = request.GET.get('country_query', '').strip()
    magic_q = request.GET.get('query', '').strip()
    
    profiles = None
    error = None
    
    # Statistiques Globales Solvable
    stats = {
        'total_signaled': IncidentReport.objects.filter(status=IncidentReport.StatusEnum.IMPACTED, is_validated=True).values('reported_tenant').distinct().count(),
        'dialogues_en_cours': IncidentReport.objects.filter(status=IncidentReport.StatusEnum.IN_MEDIATION).count(),
        'dialogues_regle': IncidentReport.objects.filter(status=IncidentReport.StatusEnum.RESOLVED).count(),
        'total_impaye': IncidentReport.objects.filter(status=IncidentReport.StatusEnum.IMPACTED, is_validated=True).aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    }
    
    recent_incidents = IncidentReport.objects.filter(is_validated=True).order_by('-created_at')[:10]
    
    if name_q or phone_q or doc_q or magic_q:
        filters = Q()
        if magic_q:
            # Recherche "Magique" pour Mobile : Nom, Tel ou Document
            filters |= Q(user__first_name__icontains=magic_q)
            filters |= Q(user__last_name__icontains=magic_q)
            filters |= Q(user__phone_number__icontains=magic_q)
            filters |= Q(user__cni_number__icontains=magic_q)
            filters |= Q(nils_number__icontains=magic_q)
        else:
            if name_q:
                filters &= (Q(user__first_name__icontains=name_q) | Q(user__last_name__icontains=name_q))
            if phone_q:
                filters &= Q(user__phone_number__icontains=phone_q)
            if doc_q:
                filters &= Q(user__cni_number__icontains=doc_q)
            if country_q:
                filters &= Q(user__document_country=country_q)
            
        profiles = NILS_Profile.objects.filter(filters).distinct()
        
        # --- SECURITY LOGGING ---
        SearchLog.objects.create(
            searcher=request.user,
            query=f"M:{magic_q}|N:{name_q}|T:{phone_q}|D:{doc_q}|C:{country_q}",
            results_found=profiles.count() if profiles else 0,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        # ------------------------
        
        if profiles and not profiles.exists():
            error = "Aucun profil Solvable n'a été trouvé avec ces critères précis."
            
    return render(request, 'nils_search.html', {
        'profiles': profiles, 
        'error': error,
        'stats': stats,
        'recent_incidents': recent_incidents,
        'countries': COUNTRY_CHOICES
    })

@login_required
def create_filiation_view(request):
    from solvable.forms import RentalFiliationForm
    from users.models import NILS_Profile
    
    # SECURITY: Only allowed for verified professionals!
    if request.user.role == 'TENANT':
        messages.error(request, "Seuls les professionnels peuvent lier un bien.")
        return redirect('dashboard')
        
    if not request.user.is_verified_pro:
        messages.error(request, f"Votre statut de {request.user.get_role_display()} doit être validé pour lier un locataire.")
        return redirect('dashboard')
        
    nils_number = request.GET.get('tenant', '').strip()
    tenant_profile = None
    
    if nils_number:
        try:
            tenant_profile = NILS_Profile.objects.get(nils_number__iexact=nils_number)
        except NILS_Profile.DoesNotExist:
            messages.error(request, "Profil NILS invalide.")
            return redirect('nils_search')
            
    if request.method == 'POST':
        form = RentalFiliationForm(request.POST, landlord=request.user)
        tenant_nils = request.POST.get('tenant_nils')
        if form.is_valid() and tenant_nils:
            try:
                t_profile = NILS_Profile.objects.get(nils_number__iexact=tenant_nils)
                filiation = form.save(commit=False)
                filiation.landlord = request.user
                filiation.tenant = t_profile.user
                filiation.save()
                messages.success(request, f"Contrat de location (Filiation) créé avec succès avec le locataire {t_profile.nils_number} !")
                return redirect('dashboard')
            except NILS_Profile.DoesNotExist:
                messages.error(request, "Locataire introuvable au moment de l'enregistrement.")
    else:
        form = RentalFiliationForm(landlord=request.user)
        
    properties_count = request.user.properties.count()
    
    return render(request, 'create_filiation.html', {
        'form': form, 
        'tenant_profile': tenant_profile,
        'properties_count': properties_count
    })

def generate_lease_pdf_view(request, filiation_id):
    """Génère un contrat de bail professionnel au format PDF le réseau de confiance Solvable."""
    from solvable.models import RentalFiliation
    from xhtml2pdf import pisa
    from io import BytesIO
    from django.template.loader import get_template
    from django.http import HttpResponse

    filiation = get_object_or_404(RentalFiliation, id=filiation_id)
    
    # Sécurité : Seuls le bailleur, le locataire ou le staff peuvent générer le document
    if request.user != filiation.landlord and request.user != filiation.tenant and not request.user.is_staff:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
        
    template = get_template('lease_agreement_pdf.html')
    context = {
        'filiation': filiation,
        'today': timezone.now(),
    }
    
    html = template.render(context)
    result = BytesIO()
    # Encodage UTF-8 pour supporter les caractères spéciaux (accents)
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        filename = f"Contrat_Bail_Solvable_{filiation.tenant.last_name}.pdf"
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    return HttpResponse("Erreur technique lors de la génération du contrat PDF. Veuillez contacter le support DigitalH.", status=500)

@login_required
def contest_item_view(request, item_type, item_id):
    from solvable.models import PaymentHistory, IncidentReport
    
    if item_type == 'payment':
        item = get_object_or_404(PaymentHistory, id=item_id)
        filiation = item.rental_filiation
    elif item_type == 'incident':
        item = get_object_or_404(IncidentReport, id=item_id)
        filiation = item.rental_filiation
    else:
        messages.error(request, "Type invalide.")
        return redirect('dashboard')
        
    # Only the tenant can contest
    if request.user != filiation.tenant:
        messages.error(request, "Seul le locataire peut contester.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        reason = request.POST.get('contestation_reason', '').strip()
        if reason:
            item.is_contested = True
            item.contestation_reason = reason
            
            # If it's an incident, automatically set status to IN_MEDIATION
            if item_type == 'incident':
                item.status = IncidentReport.StatusEnum.IN_MEDIATION
                
            item.save()
            messages.success(request, "Votre contestation a été envoyée avec succès à notre équipe de médiation. Vous pouvez maintenant discuter avec le médiateur.")
            return redirect('mediation_room', item_type=item_type, item_id=item_id)
        else:
            messages.error(request, "Veuillez fournir un motif de contestation valide.")
            
    return render(request, 'dispute_form.html', {'item': item, 'item_type': item_type, 'filiation': filiation})

@login_required
def verify_phone_view(request):
    if request.user.is_phone_verified:
        return redirect('dashboard')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'resend_otp':
            if request.user.email:
                request.user.send_otp()
                messages.success(request, f"Un nouveau code a été envoyé à {request.user.email}")
            else:
                messages.warning(request, "Veuillez d'abord ajouter un e-mail à votre profil pour recevoir le code automatiquement.")
            return redirect('verify_phone')

        user_code = request.POST.get('otp_code')
        if user_code == request.user.phone_otp:
            request.user.is_phone_verified = True
            request.user.save()
            messages.success(request, "Votre numéro de téléphone a été vérifié avec succès ! Votre profil est désormais pleinement actif.")
            return redirect('dashboard')
        else:
            messages.error(request, "Code de vérification incorrect. Veuillez contacter l'administrateur si vous ne l'avez pas reçu.")
            
    return render(request, 'verify_phone.html')

@login_required
def update_profile_view(request):
    from users.forms import UserProfileForm
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès !")
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'profile_update.html', {'form': form})

def public_profile_view(request, user_id=None, slug=None):
    from users.models import User
    from logersn.models import Property
    
    if slug:
        viewed_user = get_object_or_404(User, slug=slug)
    else:
        viewed_user = get_object_or_404(User, id=user_id)
        
    all_properties = Property.objects.filter(owner=viewed_user, is_published=True)
    properties_count = all_properties.count()
    properties = all_properties[:20]
    
    return render(request, 'public_profile.html', {
        'viewed_user': viewed_user,
        'properties': properties,
        'stats': {'total_properties': properties_count, 'experience_years': 0},
        'share_url': request.build_absolute_uri()
    })

def cgu_view(request):
    return render(request, 'legal/cgu.html')

def privacy_view(request):
    return render(request, 'legal/privacy.html')

@login_required
def toggle_favorite_view(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
    
    if not created:
        favorite.delete()
        status = 'removed'
    else:
        status = 'added'
        
    return JsonResponse({'status': status, 'count': property_obj.favorited_by.count()})

@login_required
def chat_poll_view(request, conversation_id):
    from chat.models import Conversation, Message
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Ensure user is part of the conversation
    if request.user not in conversation.participants.all() and not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    last_id = request.GET.get('last_id')
    messages_query = conversation.messages.all()
    
    if last_id:
        messages_query = messages_query.filter(id__gt=last_id)
        
    data = []
    for m in messages_query:
        data.append({
            'id': m.id,
            'sender_id': m.sender.id,
            'sender_name': "Support Logertogo" if m.sender.is_staff else str(m.sender.phone_number),
            'content': m.content,
            'created_at': m.created_at.strftime('%H:%M'),
            'is_me': m.sender == request.user
        })
        
    return JsonResponse({'messages': data})

@login_required
def report_pro_fraud_view(request):
    from solvable.forms import ProfessionalFraudReportForm
    if request.method == 'POST':
        form = ProfessionalFraudReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            from users.models import User
            pro_phone = form.cleaned_data.get('reported_pro_phone')
            if pro_phone:
                matching_user = User.objects.filter(phone_number__icontains=pro_phone).first()
                if matching_user:
                    report.reported_user = matching_user
            report.save()
            messages.success(request, "Votre signalement a été reçu et sera vérifié.")
            return redirect('fraud_list')
    else:
        form = ProfessionalFraudReportForm()
    return render(request, 'fraud_report_form.html', {'form': form})

def fraud_list_view(request):
    from solvable.models import ProfessionalFraudReport
    frauds = ProfessionalFraudReport.objects.filter(is_validated=True).order_by('-created_at')
    return render(request, 'fraud_list.html', {'frauds': frauds})

@login_required
def submit_solvency_docs_view(request):
    from users.forms import SolvencyDocumentForm
    from users.models import SolvencyDocument
    
    if request.user.role != 'TENANT':
        messages.warning(request, "Réservé aux locataires.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = SolvencyDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.user = request.user
            doc.save()
            messages.success(request, "Document soumis.")
            return redirect('dashboard')
    else:
        form = SolvencyDocumentForm()
        
    existing_docs = request.user.solvency_docs.all().order_by('-uploaded_at')
    
    return render(request, 'solvency_docs_submit.html', {'form': form, 'existing_docs': existing_docs})

# --- GUIDES D'UTILISATION (PAR PERSONA) ---

def guide_locataires_view(request):
    return render(request, 'guides/locataires.html')

def guide_bailleurs_view(request):
    return render(request, 'guides/bailleurs.html')

def guide_agences_view(request):
    return render(request, 'guides/agences.html')

def guide_courtiers_view(request):
    return render(request, 'guides/courtiers.html')


def custom_404_view(request, exception=None):
    """Gestionnaire d'erreur 404 (Page Introuvable)."""
    return render(request, '404.html', status=404)

def custom_500_view(request):
    """Gestionnaire d'erreur 500 (Erreur Serveur)."""
    return render(request, '500.html', status=500)


# ─── AVIS & NOTATIONS ──────────────────────────────────────────────────────

@login_required
def submit_review_view(request, property_id):
    """Soumettre un avis sur une annonce."""
    from logersn.models import Property, PropertyReview
    property_obj = get_object_or_404(Property, id=property_id, is_published=True)

    if request.user == property_obj.owner:
        messages.error(request, "Vous ne pouvez pas évaluer votre propre annonce.")
        return redirect('property_detail', property_id=property_id)

    if PropertyReview.objects.filter(property=property_obj, reviewer=request.user).exists():
        messages.warning(request, "Vous avez déjà soumis un avis pour cette annonce.")
        return redirect('property_detail', property_id=property_id)

    if request.method == 'POST':
        try:
            rating  = int(request.POST.get('rating', 0))
            title   = request.POST.get('title', '').strip()[:120]
            comment = request.POST.get('comment', '').strip()

            if not (1 <= rating <= 5) or not comment:
                messages.error(request, "Veuillez remplir tous les champs obligatoires.")
                return redirect(property_obj.get_absolute_url())

            PropertyReview.objects.create(
                property=property_obj,
                reviewer=request.user,
                rating=rating,
                title=title,
                comment=comment,
                is_approved=False  # Modéré par admin
            )

            # Notifier le propriétaire par email
            if property_obj.owner.email:
                try:
                    from logertogo.emails import send_review_notification
                    send_review_notification(property_obj.owner, request.user, property_obj, rating)
                except Exception:
                    pass

            messages.success(request, "Merci pour votre avis ! Il sera visible après validation par notre équipe.")
        except (ValueError, TypeError):
            messages.error(request, "Données invalides.")

    return redirect(property_obj.get_absolute_url())


# ─── ALERTES IMMOBILIÈRES ───────────────────────────────────────────────────

def subscribe_alert_view(request):
    """S'abonner aux alertes de nouvelles annonces."""
    if request.method == 'POST':
        from logersn.models import PropertyAlert
        from logersn.constants import CITY_CHOICES, PROPERTY_TYPE_CHOICES

        email     = request.POST.get('email', '').strip()
        city      = request.POST.get('city', '')
        ptype     = request.POST.get('property_type', '')
        category  = request.POST.get('listing_category', '')
        max_price = request.POST.get('max_price', '') or None

        if not email or '@' not in email:
            messages.error(request, "Veuillez saisir une adresse email valide.")
            return redirect(request.META.get('HTTP_REFERER', 'properties_list'))

        # Vérifier si l'abonnement existe déjà
        existing = PropertyAlert.objects.filter(email=email, city=city, property_type=ptype, is_active=True).first()
        if existing:
            messages.info(request, "Vous êtes déjà abonné(e) à cette alerte.")
            return redirect(request.META.get('HTTP_REFERER', 'properties_list'))

        alert = PropertyAlert.objects.create(
            email=email, city=city, property_type=ptype,
            listing_category=category, max_price=max_price or None
        )

        # Email de confirmation
        from django.conf import settings
        site_url = getattr(settings, 'SITE_URL', 'https://logertogo.com')
        unsub_url = f"{site_url}/alertes/desabonner/{alert.token}/"
        city_label = dict(CITY_CHOICES).get(city, city) or "toutes villes"
        type_label = dict(PROPERTY_TYPE_CHOICES).get(ptype, ptype) or "tous types"

        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f8f9fa;padding:20px;border-radius:12px;">
          <div style="background:linear-gradient(135deg,#0b4629,#198754);padding:24px;border-radius:8px 8px 0 0;text-align:center;">
            <h2 style="color:white;margin:0;">🔔 Alerte activée !</h2>
          </div>
          <div style="background:white;padding:28px;border-radius:0 0 8px 8px;border:1px solid #e0e0e0;">
            <p>Bonjour,</p>
            <p>Votre alerte immobilière a bien été créée. Vous serez notifié(e) dès qu'une nouvelle annonce correspondant à vos critères sera publiée :</p>
            <div style="background:#f0fdf4;border:1px solid #86efac;padding:16px;border-radius:8px;margin:16px 0;">
              <p style="margin:4px 0;"><strong>📍 Ville :</strong> {city_label}</p>
              <p style="margin:4px 0;"><strong>🏠 Type :</strong> {type_label}</p>
              {f'<p style="margin:4px 0;"><strong>💰 Budget max :</strong> {int(float(max_price)):,} FCFA</p>' if max_price else ''}
            </div>
            <p style="text-align:center;margin-top:20px;">
              <a href="{site_url}/annonces/" style="background:#198754;color:white;padding:12px 28px;border-radius:50px;text-decoration:none;font-weight:bold;display:inline-block;">
                Voir les annonces →
              </a>
            </p>
            <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
            <p style="color:#888;font-size:11px;text-align:center;">
              Pour vous désabonner : <a href="{unsub_url}" style="color:#dc3545;">Cliquer ici</a>
            </p>
          </div>
        </div>
        """
        try:
            from logertogo.emails import send_simple_email
            send_simple_email("🔔 Votre alerte immobilière | Loger Togo", html, email)
        except Exception:
            pass

        messages.success(request, f"✅ Alerte activée ! Vous serez notifié(e) à {email} pour les nouvelles annonces.")

    return redirect(request.META.get('HTTP_REFERER', 'properties_list'))


def unsubscribe_alert_view(request, token):
    """Se désabonner d'une alerte via son token unique."""
    from logersn.models import PropertyAlert
    alert = PropertyAlert.objects.filter(token=token).first()
    if alert:
        alert.is_active = False
        alert.save()
        messages.success(request, "Vous avez bien été désabonné(e) de cette alerte. Vous ne recevrez plus de notifications.")
    else:
        messages.warning(request, "Ce lien de désabonnement est invalide ou déjà utilisé.")
    return redirect('home')


def trigger_property_alerts(property_obj):
    """Déclenche l'envoi des alertes email lors de la publication d'un bien (à appeler depuis admin/payment callback)."""
    from logersn.models import PropertyAlert
    from logertogo.emails import send_new_property_alert
    from django.db.models import Q

    q = Q(is_active=True)
    if property_obj.city:
        q &= Q(city=property_obj.city) | Q(city='')
    if property_obj.property_type:
        q &= Q(property_type=property_obj.property_type) | Q(property_type='')
    if property_obj.listing_category:
        q &= Q(listing_category=property_obj.listing_category) | Q(listing_category='')

    alerts = PropertyAlert.objects.filter(q)

    # Filtrer par budget max
    eligible_emails = []
    for alert in alerts:
        if alert.max_price and property_obj.price > alert.max_price:
            continue
        eligible_emails.append(alert.email)

    if eligible_emails:
        send_new_property_alert(eligible_emails, property_obj)

    return len(eligible_emails)
