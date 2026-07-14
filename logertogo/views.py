from django.utils.translation import gettext as _
from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.db.models import Sum, Count, Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
import datetime
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging

from logersn.models import Property, Favorite, Transaction, Reservation, VisitRequest, PropertyAvailability
from management.models import HotelBooking
from logersn.forms import PropertyForm
from users.models import User, KYCProfile
from chat.models import Conversation, Message
from logersn.utils import FedaPayBridge

def home_view(request):
    """Moteur de recherche d'annonces au Togo."""
    from logersn.constants import CITY_CHOICES, PROPERTY_TYPE_CHOICES
    from django.core.paginator import Paginator

    city = request.GET.get('city')
    property_type = request.GET.get('property_type')
    listing_category = request.GET.get('listing_category')
    query = request.GET.get('query', '')

    all_properties = Property.objects.filter(is_published=True).select_related('owner').prefetch_related('images')
    if city and city != 'ALL':
        all_properties = all_properties.filter(city=city)
    if property_type and property_type != 'ALL':
        all_properties = all_properties.filter(property_type=property_type)
    if listing_category and listing_category != 'ALL':
        all_properties = all_properties.filter(listing_category=listing_category)
    if query:
        try:
            from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
            vector = SearchVector('title', weight='A') + SearchVector('neighborhood', weight='B') + SearchVector('description', weight='C')
            search_query = SearchQuery(query)
            all_properties = all_properties.annotate(
                rank=SearchRank(vector, search_query)
            ).filter(rank__gte=0.1).order_by('-rank', '-created_at')
        except Exception:
            from django.db.models import Q
            all_properties = all_properties.filter(
                Q(title__icontains=query) | Q(neighborhood__icontains=query) |
                Q(description__icontains=query) | Q(city__icontains=query)
            ).order_by('-created_at')
    else:
        all_properties = all_properties.order_by('-created_at')
    
    # Annonces boostées : carousel automatique (max 12)
    boosted_properties = Property.objects.filter(
        is_boosted=True, is_published=True
    ).select_related('owner').prefetch_related('images').order_by('-created_at')[:12]
    
    # Annonces récentes (grille statique)
    featured_properties = Property.objects.filter(is_published=True).select_related('owner').prefetch_related('images').order_by('-created_at')[:8]
    recent_properties = Property.objects.filter(is_published=True).select_related('owner').prefetch_related('images').order_by('-created_at')[:12]

    featured_pros = User.objects.filter(is_verified_pro=True).exclude(role='TENANT').order_by('?')[:12]

    return render(request, 'home.html', {
        'boosted_properties': boosted_properties,
        'featured_properties': featured_properties,
        'recent_properties': recent_properties,
        'featured_pros': featured_pros,
        'cities': CITY_CHOICES,
        'property_types': PROPERTY_TYPE_CHOICES,
        'query': query
    })

def about_view(request):
    return render(request, 'about.html')

def verified_professionals_view(request):
    pros = User.objects.filter(is_verified_pro=True).exclude(role='TENANT').order_by('company_name')
    return render(request, 'professionals_list.html', {'professionals': pros})

@login_required
def dashboard_view(request):
    """Hub central affichant les statistiques et les accès rapides (Senior UI Logic)."""
    try:
        user_properties = request.user.properties.all().prefetch_related('images').order_by('-created_at')
        
        # Statistiques pour les propriétaires
        stats_aggregation = user_properties.aggregate(total_views=Sum('views_count'))
        total_views = stats_aggregation.get('total_views') or 0
        
        # Statistiques avancées pour le tableau de bord Pro
        if request.user.role in ['HOTEL', 'AUBERGE']:
            # Gestion Hôtelière
            pending_reservations = HotelBooking.objects.filter(room__hotel=request.user, status='PENDING').count()
            total_reservations = HotelBooking.objects.filter(room__hotel=request.user).count()
        else:
            # Gestion Immobilière classique
            pending_reservations = Reservation.objects.filter(property__owner=request.user, status='PENDING').count()
            total_reservations = Reservation.objects.filter(property__owner=request.user).count()
            
        pending_visits = VisitRequest.objects.filter(property__owner=request.user, status='PENDING').count()
        pending_messages = request.user.conversations.filter(status='PENDING').count()
        
        # Pour le rôle TENANT : Récupérer ses réservations d'hôtel
        tenant_hotel_bookings = None
        if request.user.role == 'TENANT':
            tenant_hotel_bookings = HotelBooking.objects.filter(portal_client=request.user).order_by('-created_at')[:10]
        
    except Exception as e:
        # En cas d'erreur de base de données ou autre, on initialise des valeurs par défaut pour éviter le crash 500
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Dashboard View Error: {str(e)}")
        
        user_properties = request.user.properties.all().prefetch_related('images').order_by('-created_at')
        total_views, pending_reservations, total_reservations, pending_visits, pending_messages = 0, 0, 0, 0, 0
        tenant_hotel_bookings = None

    return render(request, 'dashboard.html', {
        'user_properties': user_properties,
        'total_views': total_views,
        'properties_count': user_properties.count(),
        'pending_reservations': pending_reservations,
        'total_reservations': total_reservations,
        'pending_visits': pending_visits,
        'pending_messages': pending_messages,
        'tenant_hotel_bookings': tenant_hotel_bookings,
    })

# --- PAIEMENTS FEDAPAY ---

@login_required
def initiate_payment_view(request, property_id, payment_type):
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)
    days = int(request.GET.get('days', 1)) 
    transaction = FedaPayBridge.initiate_transaction(request.user, payment_type, property_obj, days)
    
    if transaction.amount <= 0:
        return redirect(f"/paiement/callback/?ref={transaction.reference}&status=success")
        
    payment_url = FedaPayBridge.generate_payment_url(transaction)
    return redirect(payment_url)

@login_required
def checkout_payment_view(request, property_id, payment_type):
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)
    pricing = FedaPayBridge.get_pricing()
    
    unit_price = pricing.get('boost', 0)
    if payment_type == 'PUBLICATION':
        unit_price = pricing.get(f'publication_{property_obj.listing_category.lower()}', pricing.get('publication_rent', 0))
    
    return render(request, 'checkout.html', {
        'property': property_obj,
        'payment_type': payment_type,
        'unit_price': unit_price,
        'config': pricing
    })

def payment_callback_view(request):
    """
    Callback sécurisé pour le retour de FedaPay.
    DigitalH Security: Vérification du statut pour éviter les injections URL.
    """
    ref = request.GET.get('ref')
    status = request.GET.get('status')
    
    if not ref or not status:
        messages.error(request, _("Paramètres de paiement manquants."))
        return redirect('dashboard')
        
    transaction = get_object_or_404(Transaction, reference=ref)
    
    # Sécurité : Si déjà validé, on ne retraite pas
    if transaction.status == 'SUCCESS':
        messages.warning(request, _("Cette transaction a déjà été confirmée."))
        return redirect('dashboard')

    # DigitalH Security: Vérification réelle côté serveur
    is_valid, transaction = FedaPayBridge.verify_transaction(ref)
    
    if is_valid and status == 'success':
        transaction.status = 'SUCCESS'
        transaction.save()
        
        # Actions selon le type de transaction
        if transaction.transaction_type == 'PUBLICATION' and transaction.property:
            transaction.property.is_published = True
            transaction.property.is_paid = True  # Indispensable pour la validation DigitalH
            transaction.property.save()
            messages.success(request, _("Paiement réussi ! Votre annonce est maintenant en ligne."))
            
        elif transaction.transaction_type == 'BOOST' and transaction.property:
            transaction.property.is_boosted = True
            transaction.property.boost_until = timezone.now() + datetime.timedelta(days=transaction.days)
            transaction.property.save()
            messages.success(request, _("Annonce boostée pour %(days)s jours !") % {'days': transaction.days})
            
        return render(request, 'payment_success.html', {'transaction': transaction})
    
    transaction.status = 'FAILED'
    transaction.save()
    messages.error(request, _("Le paiement a échoué ou a été annulé."))
    return redirect('dashboard')

@csrf_exempt
@require_POST
def fedapay_webhook_view(request):
    """
    Endpoint sécurisé pour les Webhooks FedaPay (S2S).
    Permet de valider un paiement même si l'utilisateur quitte la page.
    """
    logger = logging.getLogger(__name__)
    try:
        payload = json.loads(request.body)
        event_type = payload.get('name', '')
        
        if event_type == 'transaction.approved':
            entity = payload.get('entity', {})
            # Dans certains cas de webhooks FedaPay, c'est entity.custom_metadata.reference
            # ou bien simplement la référence sur la transaction
            custom_metadata = entity.get('custom_metadata', {})
            ref = custom_metadata.get('reference')
            
            if not ref:
                logger.error("Webhook FedaPay: Référence introuvable dans le payload.")
                return HttpResponse(status=400)
                
            transaction = Transaction.objects.filter(reference=ref).first()
            if not transaction:
                logger.error(f"Webhook FedaPay: Transaction introuvable pour {ref}.")
                return HttpResponse(status=404)
                
            if transaction.status == 'SUCCESS':
                # Déjà validé
                return HttpResponse(status=200)

            # DigitalH Security: On vérifie tout de même via l'API pour être certain
            is_valid, _ = FedaPayBridge.verify_transaction(ref)
            
            if is_valid:
                transaction.status = 'SUCCESS'
                transaction.save()
                
                # Actions selon le type de transaction
                if transaction.transaction_type == 'PUBLICATION' and transaction.property:
                    transaction.property.is_published = True
                    transaction.property.is_paid = True
                    transaction.property.save()
                    logger.info(f"Webhook FedaPay: Publication activée pour la transaction {ref}")
                    
                elif transaction.transaction_type == 'BOOST' and transaction.property:
                    transaction.property.is_boosted = True
                    transaction.property.boost_until = timezone.now() + datetime.timedelta(days=transaction.days)
                    transaction.property.save()
                    logger.info(f"Webhook FedaPay: Boost activé pour la transaction {ref}")
                    
            return HttpResponse(status=200)
            
        return HttpResponse(status=200) # Evènement non géré, on répond OK
        
    except json.JSONDecodeError:
        return HttpResponse(status=400)
    except Exception as e:
        logger.error(f"Webhook FedaPay Erreur Globale: {str(e)}")
        return HttpResponse(status=500)


@login_required
def payment_success_view(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    return render(request, 'payment_success.html', {'transaction': transaction})

@login_required
def payment_request_sent_view(request):
    ref = request.GET.get('ref')
    transaction = get_object_or_404(Transaction, reference=ref, user=request.user)
    return render(request, 'payment_request_sent.html', {'transaction': transaction})

# --- AUTRES ---

def cgu_view(request): return render(request, 'legal/cgu.html')
def privacy_view(request): return render(request, 'legal/privacy.html')

def custom_404_view(request, exception): return render(request, '404.html', status=404)
def custom_500_view(request): return render(request, '500.html', status=500)

@login_required
def kyc_submit_view(request):
    from users.forms import KYCProfileForm
    kyc, created = KYCProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = KYCProfileForm(request.POST, request.FILES, instance=kyc)
        if form.is_valid():
            form.save()
            messages.success(request, _("Documents KYC soumis avec succès !"))
            return redirect('dashboard')
    else:
        form = KYCProfileForm(instance=kyc)
    return render(request, 'kyc_submit.html', {'form': form})

def guide_locataires_view(request): return render(request, 'guides/locataires.html')
def guide_bailleurs_view(request): return render(request, 'guides/bailleurs.html')
def guide_agences_view(request): return render(request, 'guides/agences.html')
def guide_courtiers_view(request): return render(request, 'guides/courtiers.html')

@login_required
def start_support_view(request):
    """Initialise ou récupère une discussion privée avec le support technique."""
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        messages.error(request, _("Service support indisponible."))
        return redirect('dashboard')
    
    # Chercher une conversation de type SUPPORT où l'utilisateur est participant
    conversation = Conversation.objects.filter(
        topic=Conversation.TopicEnum.SUPPORT,
        participants=request.user
    ).first()

    if not conversation:
        conversation = Conversation.objects.create(
            topic=Conversation.TopicEnum.SUPPORT,
            status=Conversation.StatusEnum.ACCEPTED # Le support est auto-accepté
        )
        conversation.participants.add(request.user, admin_user)
        
    return redirect(f"{reverse('messagerie')}?conv={conversation.id}")

@login_required
def chat_poll_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    messages_qs = conversation.messages.all().order_by('created_at')
    return render(request, 'partials/chat_messages.html', {'messages': messages_qs})
