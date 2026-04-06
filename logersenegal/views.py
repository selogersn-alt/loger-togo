from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
import datetime
from logersn.models import Property
from logersn.forms import PropertyForm
from users.models import User, NILS_Profile
from chat.models import Conversation, Message
from solvable.models import PropertyApplication, RentalFiliation, PaymentHistory
from logersn.models import Favorite
from django.http import JsonResponse

def home_view(request):
    featured_properties = Property.objects.filter(is_published=True).order_by('-created_at')[:3]
    boosted_properties = Property.objects.filter(is_published=True, is_boosted=True).order_by('?')[:12]
    return render(request, 'home.html', {
        'featured_properties': featured_properties,
        'boosted_properties': boosted_properties
    })

def about_view(request):
    return render(request, 'about.html')

def verified_professionals_view(request):
    # Les pros vérifiés par l'admin (badge is_verified_pro=True) et qui sont Agency, Broker, Agent, Landlord
    pros = User.objects.filter(is_verified_pro=True).exclude(role='TENANT').order_by('role', 'company_name', 'phone_number')
    
    context = {
        'professionals': pros
    }
    return render(request, 'professionals_list.html', context)

def properties_list_view(request):
    # Récupérer les paramètres de recherche
    city = request.GET.get('city')
    neighborhood = request.GET.get('neighborhood')
    property_type = request.GET.get('property_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Base Queryset
    properties = Property.objects.filter(is_published=True)
    
    # Filtrage
    if city and city != 'ALL':
        properties = properties.filter(city=city)
    if neighborhood and neighborhood != 'ALL':
        properties = properties.filter(neighborhood=neighborhood)
    if property_type and property_type != 'ALL':
        properties = properties.filter(property_type=property_type)
    if min_price:
        properties = properties.filter(rent_price__gte=min_price)
    if max_price:
        properties = properties.filter(rent_price__lte=max_price)
        
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
        properties = properties.order_by('-is_boosted', 'rent_price')
    elif sort == 'price_desc':
        properties = properties.order_by('-is_boosted', '-rent_price')
    else:
        properties = properties.order_by('-is_boosted', '-created_at')
        
    # Extraire les annonces pour le bandeau défilant du haut (Boostées uniquement)
    boosted_slider = Property.objects.filter(is_published=True, is_boosted=True).order_by('?')[:5]
    
    from logersn.constants import CITY_CHOICES, PROPERTY_TYPE_CHOICES, NEIGHBORHOOD_CHOICES
    
    context = {
        'properties': properties,
        'boosted_slider': boosted_slider,
        'cities': CITY_CHOICES,
        'neighborhoods': NEIGHBORHOOD_CHOICES,
        'property_types': PROPERTY_TYPE_CHOICES,
        'current_filters': request.GET
    }
    
    return render(request, 'properties_list.html', context)

def property_detail_view(request, property_id):
    # Récupère l'annonce par son ID unique de base de données (UUID)
    property_obj = get_object_or_404(Property, id=property_id, is_published=True)
    
    # Incrémentation des statistiques de vue (Analytics)
    property_obj.views_count += 1
    property_obj.save()
    
    # Biens similaires (même ville ou même type)
    related_properties = Property.objects.filter(
        is_published=True
    ).filter(
        models.Q(city=property_obj.city) | models.Q(property_type=property_obj.property_type)
    ).exclude(id=property_obj.id)[:4]
    
    context = {
        'property': property_obj,
        'related_properties': related_properties
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
            return redirect('dashboard') # Redirect to dashboard instead of home
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
        messages.success(request, "Votre compte a été créé avec succès !")
        return redirect('dashboard')
        
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('home')

@login_required
def dashboard_view(request):
    # Retrieve conversations for the logged in user to display in the chat tab
    conversations = request.user.conversations.prefetch_related('messages').all()
    
    # Gerer le chat actif via l'URL (ex: ?conv=ID_DE_LA_CONV)
    active_conv_id = request.GET.get('conv')
    active_conversation = None
    
    if active_conv_id:
        active_conversation = conversations.filter(id=active_conv_id).first()
    elif conversations.exists():
        active_conversation = conversations.first()
    
    from solvable.models import PropertyApplication, RentalFiliation
    
    properties = request.user.properties.all()
    approved_properties = properties.filter(is_published=True)
    pending_properties = properties.filter(is_published=False)
    
    # Applications sent by user (Tenant role)
    my_applications = request.user.my_applications.all().order_by('-created_at')
    
    # Applications received for user's properties (Pro roles)
    received_applications = PropertyApplication.objects.filter(property__owner=request.user).order_by('-created_at')
    
    # Pendings filiations to approve
    pending_approvals = request.user.tenant_filiations.filter(status=RentalFiliation.StatusEnum.PENDING_APPROVAL)
    
    context = {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'properties': properties,
        'approved_count': approved_properties.count(),
        'pending_count': pending_properties.count(),
        'my_applications': my_applications,
        'received_applications': received_applications,
        'pending_approvals': pending_approvals,
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
                
            messages.info(request, "Annonce enregistrée ! Veuillez procéder au paiement des frais de publication (100F) pour l'activer.")
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
    if payment_type == 'PUBLICATION': unit_price = pricing['publication']
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
    return render(request, 'recovery.html')

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
        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
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
    from users.models import NILS_Profile
    
    # SECURITY: Only allowed for Pros!
    if request.user.role == 'TENANT' and not request.user.is_staff:
        messages.error(request, "Accès réservé aux bailleurs et agences professionnels.")
        return redirect('dashboard')
        
    query = request.GET.get('query', '').strip()
    profiles = []
    error = None
    
    if query:
        from django.db.models import Q
        from users.models import SearchLog
        try:
            # Recherche ultra-large pour identifier les mauvais payeurs
            profiles = NILS_Profile.objects.filter(
                Q(nils_number__iexact=query) | 
                Q(user__phone_number__contains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__cni_number__iexact=query) |
                Q(user__employer__icontains=query) |
                Q(user__spouse_name__icontains=query)
            ).distinct()
            
            # --- SECURITY LOGGING ---
            SearchLog.objects.create(
                searcher=request.user,
                query=query,
                results_found=profiles.count(),
                ip_address=request.META.get('REMOTE_ADDR')
            )
            # ------------------------
            
            if not profiles.exists():
                error = f"Aucun profil Solvable n'a été trouvé pour '{query}'."
        except Exception as e:
            error = f"Erreur lors de la recherche : {str(e)}"
            
    return render(request, 'nils_search.html', {'query': query, 'profiles': profiles, 'error': error})

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

@login_required
def report_incident_view(request):
    from solvable.forms import IncidentReportForm
    from solvable.models import RentalFiliation
    
    filiation_id = request.GET.get('filiation', None)
    
    if request.method == 'POST':
        form = IncidentReportForm(request.POST, landlord=request.user)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reporter = request.user
            incident.reported_tenant = incident.rental_filiation.tenant
            # Default status is IN_MEDIATION
            incident.save()
            messages.success(request, f"L'incident a été déclaré avec succès. Il est en cours de médiation pour le locataire au profil NILS associé.")
            return redirect('dashboard')
    else:
        initial_data = {}
        if filiation_id:
            initial_data['rental_filiation'] = filiation_id
        form = IncidentReportForm(landlord=request.user, initial=initial_data)
        
    has_filiations = RentalFiliation.objects.filter(landlord=request.user, status=RentalFiliation.StatusEnum.ACTIVE).exists()
    
    return render(request, 'report_incident.html', {'form': form, 'has_filiations': has_filiations})

@login_required
def record_payment_view(request):
    from solvable.forms import PaymentHistoryForm
    from solvable.models import RentalFiliation
    filiation_id = request.GET.get('filiation', None)
    
    if request.method == 'POST':
        # request.FILES must be passed to read file uploads
        form = PaymentHistoryForm(request.POST, request.FILES, landlord=request.user)
        if form.is_valid():
            payment = form.save(commit=False)
            # Make sure to default the month_year day to the 1st
            if payment.month_year:
                payment.month_year = payment.month_year.replace(day=1)
            payment.payment_date = datetime.date.today()
            payment.save()
            messages.success(request, f"Le paiement a été enregistré avec succès pour {payment.month_year.strftime('%B %Y')}.")
            return redirect('dashboard')
    else:
        initial_data = {}
        if filiation_id:
            initial_data['rental_filiation'] = filiation_id
        form = PaymentHistoryForm(landlord=request.user, initial=initial_data)
        
    has_filiations = RentalFiliation.objects.filter(landlord=request.user, status=RentalFiliation.StatusEnum.ACTIVE).exists()
    
    return render(request, 'record_payment.html', {'form': form, 'has_filiations': has_filiations})

@login_required
def filiation_details_view(request, filiation_id):
    from solvable.models import RentalFiliation
    
    filiation = get_object_or_404(RentalFiliation, id=filiation_id)
    
    # Security: only landlord or tenant can see it
    if request.user != filiation.landlord and request.user != filiation.tenant:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
        
    payments = filiation.payments.all().order_by('-created_at')
    incidents = filiation.incidents.all().order_by('-created_at')
    
    context = {
        'filiation': filiation,
        'payments': payments,
        'incidents': incidents,
        'is_tenant': request.user == filiation.tenant,
        'is_landlord': request.user == filiation.landlord
    }
    return render(request, 'filiation_details.html', context)

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
def update_incident_status_view(request):
    from solvable.models import IncidentReport
    
    if request.method == 'POST' and request.user.is_staff:
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')
        
        incident = get_object_or_404(IncidentReport, id=item_id)
        
        if action == 'resolve':
            incident.status = IncidentReport.StatusEnum.RESOLVED
            messages.success(request, "L'incident a été marqué comme RÉSOLU. Le score du locataire a été mis à jour (+29% récupérés).")
        elif action == 'impact':
            incident.status = IncidentReport.StatusEnum.IMPACTED
            messages.warning(request, "Le signalement a été confirmé comme IMPACTANT. Le score du locataire reste bas.")
            
        incident.save()
        
        # Update user score
        if hasattr(incident.reported_tenant, 'nils_profiles'):
             for profile in incident.reported_tenant.nils_profiles.all():
                 profile.update_score()
                 
        return redirect('mediation_room', item_type='incident', item_id=item_id)
        
    messages.error(request, "Action non autorisée.")
    return redirect('dashboard')

@login_required
def mediation_room_view(request, item_type, item_id):
    from solvable.models import PaymentHistory, IncidentReport, MediationMessage
    
    if item_type == 'payment':
        item = get_object_or_404(PaymentHistory, id=item_id)
        filiation = item.rental_filiation
    elif item_type == 'incident':
        item = get_object_or_404(IncidentReport, id=item_id)
        filiation = item.rental_filiation
    else:
        messages.error(request, "Type invalide.")
        return redirect('dashboard')
        
    # Security: only parties involved can see the mediation (Tenant, Landlord, or Staff/Mediator)
    if request.user != filiation.tenant and request.user != filiation.landlord and not request.user.is_staff:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            msg = MediationMessage(
                sender=request.user,
                content=content,
                is_from_mediator=request.user.is_staff
            )
            if item_type == 'payment':
                msg.payment = item
            else:
                msg.incident = item
            msg.save()
            
            # Re-calculate score in case the status was changed in the mean time
            if hasattr(request.user, 'nils_profile'):
                request.user.nils_profile.update_score()
                
            messages.success(request, "Message envoyé.")
            return redirect('mediation_room', item_type=item_type, item_id=item_id)
            
    messages_list = item.mediation_messages.all().order_by('created_at') if hasattr(item, 'mediation_messages') else []
    
    context = {
        'item': item,
        'item_type': item_type,
        'filiation': filiation,
        'mediation_messages': messages_list,
        'is_mediator': request.user.is_staff
    }
    return render(request, 'mediation_room.html', context)

from django.http import HttpResponse

@login_required
def download_receipt_view(request, payment_id):
    from solvable.models import PaymentHistory
    from .utils_pdf import generate_receipt_pdf
    
    payment = get_object_or_404(PaymentHistory, id=payment_id)
    filiation = payment.rental_filiation
    
    # Sécurité : Seules les parties du contrat peuvent télécharger
    if request.user != filiation.tenant and request.user != filiation.landlord and not request.user.is_staff:
        messages.error(request, "Accès non autorisé à cette quittance.")
        return redirect('dashboard')
        
    # Ne permettre le téléchargement que si le paiement est confirmé (statut PAID)
    if payment.status != PaymentHistory.StatusEnum.PAID:
        messages.warning(request, "Cette quittance ne peut être générée avant confirmation du paiement.")
        return redirect('filiation_details', filiation_id=filiation.id)

    pdf_buffer = generate_receipt_pdf(payment)
    filename = f"Quittance_Solvable_{payment.month_year.replace('/', '_')}.pdf"
    
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
@login_required
def apply_to_property_view(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id, is_published=True)
    
    nils = request.user.nils_profile
    if not nils:
        messages.warning(request, "Pour postuler, vous devez d'abord créer votre profil NILS (numéro d'identification locative).")
        return redirect('dashboard')
    
    # Check if already applied
    if PropertyApplication.objects.filter(property=property_obj, applicant=request.user).exists():
        messages.info(request, "Vous avez déjà postulé pour ce bien. L'agent étudie votre dossier.")
        return redirect('property_detail', property_id=property_id)
    
    # Create application
    PropertyApplication.objects.create(
        property=property_obj,
        applicant=request.user,
        message=f"Bonjour, je suis intéressé par votre annonce : {property_obj.title}. Voici mon numéro NILS : {nils.nils_number}"
    )
    
    messages.success(request, f"Votre candidature pour '{property_obj.title}' a été envoyée avec succès !")
    return redirect('dashboard')

@login_required
def start_filiation_view(request, application_id):
    from solvable.models import PropertyApplication, RentalFiliation
    from users.models import NILS_Profile
    
    application = get_object_or_404(PropertyApplication, id=application_id, applicant=request.user)
    
    # Vérifier que la candidature est acceptée par l'agent
    if application.status != PropertyApplication.StatusEnum.ACCEPTED:
        messages.warning(request, "Votre candidature n'a pas encore été acceptée par le bailleur.")
        return redirect('dashboard')
    
    # Vérifier si une filiation existe déjà pour cette candidature
    if RentalFiliation.objects.filter(property=application.property, tenant=request.user).exclude(status=RentalFiliation.StatusEnum.TERMINATED).exists():
        messages.warning(request, "Un contrat est déjà lié à cette annonce.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        landlord_nils = request.POST.get('landlord_nils')
        try:
            # On cherche un profil bailleur ou agence
            nils_profile = NILS_Profile.objects.exclude(nils_type='TENANT').get(nils_number=landlord_nils)
            landlord = nils_profile.user
            
            # Bloquer l'auto-liaison
            if landlord == request.user:
                messages.error(request, "Vous ne pouvez pas être votre propre bailleur.")
                return redirect('dashboard')
            
            # Création de la filiation en attente
            RentalFiliation.objects.create(
                property=application.property,
                landlord=landlord,
                tenant=request.user,
                monthly_rent=application.property.rent_price,
                start_date=timezone.now().date(),
                status=RentalFiliation.StatusEnum.PENDING_APPROVAL
            )
            
            # Marquer la candidature comme acceptée
            application.status = PropertyApplication.StatusEnum.ACCEPTED
            application.save()
            
            messages.success(request, f"Demande de liaison envoyée à {landlord.phone_number}. Le bailleur doit maintenant approuver pour activer le contrat.")
            return redirect('dashboard')
        except NILS_Profile.DoesNotExist:
            messages.error(request, f"Numéro NILS '{landlord_nils}' invalide ou n'est pas un profil bailleur/agence.")
            
    return render(request, 'start_filiation.html', {'application': application})

@login_required
def approve_filiation_view(request, filiation_id):
    from solvable.models import RentalFiliation
    filiation = get_object_or_404(RentalFiliation, id=filiation_id, landlord=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            filiation.status = RentalFiliation.StatusEnum.ACTIVE
            filiation.save()
            messages.success(request, "Le contrat est désormais actif ! Vous pouvez maintenant enregistrer les paiements.")
        else:
            filiation.delete()
            messages.warning(request, "La demande de liaison a été rejetée.")
        return redirect('dashboard')
        
    return render(request, 'approve_filiation.html', {'filiation': filiation})

@login_required
def terminate_filiation_view(request, filiation_id):
    from solvable.models import RentalFiliation
    filiation = get_object_or_404(RentalFiliation, id=filiation_id)
    
    # Sécurité: seules les parties du contrat peuvent agir
    if request.user != filiation.landlord and request.user != filiation.tenant:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        rating = request.POST.get('rating')
        if not rating:
            messages.error(request, "La notation est obligatoire pour clore un contrat de confiance.")
            return redirect('terminate_filiation', filiation_id=filiation.id)
            
        try:
            rating_val = int(rating)
            # Enregistrer la note pour l'AUTRE partie
            if request.user == filiation.tenant:
                filiation.rating_for_landlord = rating_val
            else:
                filiation.rating_for_tenant = rating_val
            
            # Logique de changement de statut
            if filiation.status == RentalFiliation.StatusEnum.ACTIVE:
                # Premier demandeur
                filiation.status = RentalFiliation.StatusEnum.TERMINATION_REQUESTED
                messages.info(request, "Demande de résiliation enregistrée. L'autre partie doit confirmer.")
            elif filiation.status == RentalFiliation.StatusEnum.TERMINATION_REQUESTED:
                # Deuxième confirmation
                filiation.status = RentalFiliation.StatusEnum.TERMINATED
                filiation.end_date = timezone.now().date()
                messages.success(request, "Le contrat est désormais terminé et archivé.")
                
            filiation.save()
            return redirect('dashboard')
            
        except ValueError:
            messages.error(request, "Note invalide.")
            
    return render(request, 'terminate_filiation.html', {'filiation': filiation})

@login_required
def update_application_status_view(request, application_id):
    from solvable.models import PropertyApplication
    # Check that current user is the owner of the property
    application = get_object_or_404(PropertyApplication, id=application_id, property__owner=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            application.status = PropertyApplication.StatusEnum.ACCEPTED
            messages.success(request, f"Candidature de {application.applicant.phone_number} acceptée !")
        elif action == 'reject':
            application.status = PropertyApplication.StatusEnum.REJECTED
            messages.warning(request, "Candidature refusée.")
        application.save()
        
    return redirect('dashboard')

@login_required
def verify_phone_view(request):
    if request.user.is_phone_verified:
        return redirect('dashboard')
        
    if request.method == 'POST':
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
def update_application_status_view(request, application_id):
    from solvable.models import PropertyApplication
    application = get_object_or_404(PropertyApplication, id=application_id, property__owner=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            application.status = 'ACCEPTED'
            messages.success(request, f"Candidature acceptée ! Le locataire peut désormais finaliser son bail.")
        elif action == 'reject':
            application.status = 'REJECTED'
            messages.warning(request, f"Candidature rejetée.")
        
        application.save()
        
    return redirect('dashboard')

@login_required
def public_profile_view(request, user_id):
    from users.models import User
    from logersn.models import Property
    from django.shortcuts import get_object_or_404
    
    viewed_user = get_object_or_404(User, id=user_id)
    properties = Property.objects.filter(owner=viewed_user, is_published=True)
    
    # Statistiques basiques d'activité
    stats = {
        'total_properties': properties.count(),
        'experience_years': (timezone.now() - viewed_user.date_joined).days // 365,
    }
    
    return render(request, 'public_profile.html', {
        'viewed_user': viewed_user,
        'properties': properties,
        'stats': stats
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
            'sender_name': "Support Logersenegal" if m.sender.is_staff else str(m.sender.phone_number),
            'content': m.content,
            'created_at': m.created_at.strftime('%H:%M'),
            'is_me': m.sender == request.user
        })
        
    return JsonResponse({'messages': data})
