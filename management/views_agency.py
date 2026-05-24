import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from django.urls import reverse
from django.conf import settings
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime

from django.contrib.auth import get_user_model, authenticate, login, logout
from .models import Lease, RentPayment, AgencyClient, MaintenanceRequest, ContractTemplate, PropertyInventory
from logersn.models import Property

User = get_user_model()

def agency_saas_required(view_func):
    """
    Decorator to ensure user is logged in and has active SaaS subscription.
    Otherwise redirects to the agency login page.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            next_url = request.build_absolute_uri()
            return redirect(f"{reverse('agency_login')}?next={next_url}")
            
        if not request.user.is_saas_active:
            # Redirect to agency landing/promo page
            return redirect('agency_promo')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def agency_login(request):
    """
    Premium login view for the agency subdomain.
    """
    if request.user.is_authenticated:
        if request.user.is_saas_active:
            return redirect('agency_dashboard')
        return redirect('agency_promo')
        
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, "Veuillez remplir tous les champs.")
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user, backend='users.backends.PhoneOrEmailBackend')
                messages.success(request, f"Ravi de vous revoir, {user.get_full_name()} !")
                
                if next_url:
                    return redirect(next_url)
                if user.is_saas_active:
                    return redirect('agency_dashboard')
                return redirect('agency_promo')
            else:
                messages.error(request, "Identifiants incorrects ou compte inexistant.")
                
    return render(request, 'agency/login.html', {'next': next_url})


def agency_register(request):
    """
    Premium registration view for the agency subdomain.
    """
    if request.user.is_authenticated:
        if request.user.is_saas_active:
            return redirect('agency_dashboard')
        return redirect('agency_promo')
        
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        role = request.POST.get('role', User.RoleEnum.AGENCY)
        company_name = request.POST.get('company_name', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        coverage_area = request.POST.get('coverage_area', '')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if not phone_number and not email:
            messages.error(request, "Vous devez fournir au moins un numéro de téléphone ou un e-mail.")
        elif not password or not password_confirm:
            messages.error(request, "Veuillez saisir votre mot de passe et sa confirmation.")
        elif password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        else:
            phone_exists = phone_number and User.objects.filter(phone_number=phone_number).exists()
            email_exists = email and User.objects.filter(email=email).exists()
            
            if phone_exists:
                messages.error(request, "Ce numéro de téléphone est déjà associé à un compte.")
            elif email_exists:
                messages.error(request, "Cette adresse e-mail est déjà associée à un compte.")
            else:
                try:
                    user = User.objects.create_user(
                        phone_number=phone_number or None,
                        password=password,
                        email=email or None,
                        role=role,
                        company_name=company_name,
                        first_name=first_name,
                        last_name=last_name,
                        coverage_area=coverage_area
                    )
                    login(request, user, backend='users.backends.PhoneOrEmailBackend')
                    messages.success(request, "Votre compte agence a été créé avec succès !")
                    return redirect('agency_promo')
                except Exception as e:
                    messages.error(request, f"Erreur lors de l'inscription : {str(e)}")
                    
    context = {
        'roles': User.RoleEnum.choices,
    }
    return render(request, 'agency/register.html', context)


def agency_logout(request):
    """
    Logout view for the agency subdomain.
    """
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('agency_promo')


def agency_promo(request):
    """
    Premium Landing/Marketing page for non-subscribed users or prospects.
    """
        
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, "Veuillez vous connecter ou créer un compte pour lancer votre essai gratuit de 15 jours.")
            return redirect(f"{reverse('agency_login')}?next={reverse('agency_promo')}")
            
        request.user.is_saas_active = True
        request.user.save()
        messages.success(request, "Félicitations ! Votre essai de 15 jours a été activé avec succès. Bienvenue dans votre Espace Agence CRM !")
        return redirect('agency_dashboard')
        
    return render(request, 'agency/agency_promo.html')


def explications_view(request):
    """
    Page d'explication des fonctionnalités de l'Espace Gérance Pro.
    """
    return render(request, 'agency/explications.html')


def agency_privacy_view(request):
    """
    Page de politique de confidentialité pour les professionnels (RGPD & normes internationales).
    """
    return render(request, 'agency/confidentialite.html')


@agency_saas_required
def agency_dashboard(request):
    """
    Main SaaS Dashboard for the agency with Advanced Statistics.
    """
    agency = request.user
    
    # 1. Calculations & Metrics
    total_clients = AgencyClient.objects.filter(agency=agency).count()
    total_properties = Property.objects.filter(owner=agency).count()
    
    # Leases where agency is landlord
    my_leases = Lease.objects.filter(landlord=agency)
    total_leases = my_leases.count()
    active_leases_count = my_leases.filter(status=Lease.StatusEnum.ACTIVE).count()
    
    # Occupancy Rate (taux d'occupation)
    occupancy_rate = 0
    if total_properties > 0:
        occupied_properties_count = my_leases.filter(status=Lease.StatusEnum.ACTIVE).values('property').distinct().count()
        occupancy_rate = round((occupied_properties_count / total_properties) * 100, 1)
        
    # Collected rent revenue (Total payments where status is PAID or PARTIAL)
    payments = RentPayment.objects.filter(lease__landlord=agency)
    total_revenue = payments.filter(status=RentPayment.StatusEnum.PAID).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    # Outstanding/Unpaid rents
    unpaid_payments = payments.filter(status=RentPayment.StatusEnum.UNPAID)
    total_unpaid = unpaid_payments.aggregate(total=Sum('amount_due'))['total'] or 0
    
    # Recent clients
    recent_clients = AgencyClient.objects.filter(agency=agency).order_by('-created_at')[:5]
    
    # Recent payments
    recent_payments = list(payments.order_by('-period_start')[:5])
    today = timezone.now().date()
    for p in recent_payments:
        due_day = p.lease.payment_due_day
        try:
            due_date = p.period_start.replace(day=due_day)
        except ValueError:
            due_date = p.period_start.replace(day=28)
        p.is_overdue = (p.status != RentPayment.StatusEnum.PAID) and (today > due_date)
    
    # Pipeline clients count for pipeline mini-summary
    pipeline_stats = AgencyClient.objects.filter(agency=agency).values('pipeline_stage').annotate(count=Count('id'))
    pipeline_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for stat in pipeline_stats:
        stage = stat['pipeline_stage']
        if stage in pipeline_counts:
            pipeline_counts[stage] = stat['count']
            
    # Monthly collected revenues (actual if payments exist)
    months_labels = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    monthly_data = [0] * 12
    for p in payments.filter(status=RentPayment.StatusEnum.PAID, date_paid__isnull=False):
        month_idx = p.date_paid.month - 1
        monthly_data[month_idx] += float(p.amount_paid)

    # Property category breakdown for advanced visual analysis
    categories_stats = Property.objects.filter(owner=agency).values('listing_category').annotate(count=Count('id'))
    categories_data = {'RENT': 0, 'SALE': 0, 'FURNISHED': 0}
    for item in categories_stats:
        cat = item['listing_category']
        if cat in categories_data:
            categories_data[cat] = item['count']

    context = {
        'total_clients': total_clients,
        'total_properties': total_properties,
        'total_leases': total_leases,
        'active_leases_count': active_leases_count,
        'occupancy_rate': occupancy_rate,
        'total_revenue': total_revenue,
        'total_unpaid': total_unpaid,
        'recent_clients': recent_clients,
        'recent_payments': recent_payments,
        'pipeline_counts': pipeline_counts,
        'months_labels': months_labels,
        'monthly_data': monthly_data,
        'categories_data': categories_data,
    }
    return render(request, 'agency/agency_dashboard.html', context)


@agency_saas_required
def agency_clients(request):
    """
    Client CRM sheet manager. List and create clients.
    """
    agency = request.user
    query = request.GET.get('q', '')
    client_type = request.GET.get('type', '')
    
    clients_qs = AgencyClient.objects.filter(agency=agency)
    
    if query:
        clients_qs = clients_qs.filter(full_name__icontains=query) | clients_qs.filter(phone__icontains=query) | clients_qs.filter(email__icontains=query)
    
    if client_type:
        clients_qs = clients_qs.filter(client_type=client_type)
        
    clients = clients_qs.order_by('-created_at')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        c_type = request.POST.get('client_type', AgencyClient.ClientType.TENANT)
        status = request.POST.get('status', AgencyClient.ClientStatus.PROSPECT)
        notes = request.POST.get('notes', '')
        
        if full_name and phone:
            client = AgencyClient.objects.create(
                agency=agency,
                full_name=full_name,
                email=email if email else None,
                phone=phone,
                client_type=c_type,
                status=status,
                notes=notes
            )
            
            # Create a phantom user so they can be selected for leases
            if c_type == AgencyClient.ClientType.TENANT:
                try:
                    tenant_user, created = User.objects.get_or_create(
                        phone_number=phone,
                        defaults={
                            'first_name': full_name.split()[0] if ' ' in full_name else full_name,
                            'last_name': ' '.join(full_name.split()[1:]) if ' ' in full_name else '',
                            'email': email if email else None,
                            'role': User.RoleEnum.TENANT,
                            'parent_agency': agency
                        }
                    )
                    if created:
                        tenant_user.set_password(User.objects.make_random_password())
                        tenant_user.save()
                except Exception as e:
                    pass
            
            messages.success(request, f"Client {client.full_name} créé avec succès.")
            return redirect('agency_clients')
        else:
            messages.error(request, "Veuillez remplir au moins le nom complet et le numéro de téléphone.")
            
    context = {
        'clients': clients,
        'query': query,
        'client_type': client_type,
        'types': AgencyClient.ClientType.choices,
        'statuses': AgencyClient.ClientStatus.choices,
    }
    return render(request, 'agency/agency_clients.html', context)


@agency_saas_required
def agency_pipeline(request):
    """
    Visual Kanban Deal stage manager.
    Stages: 
    1: Prospecting (Prospect)
    2: Contacted (Prise de contact)
    3: Visit Scheduled (Visite planifiée)
    4: Negotiation (Négociation)
    5: Signed (Contrat signé)
    """
    agency = request.user
    clients = AgencyClient.objects.filter(agency=agency)
    
    stages = {
        1: {'name': 'Prospection', 'clients': clients.filter(pipeline_stage=1)},
        2: {'name': 'Prise de contact', 'clients': clients.filter(pipeline_stage=2)},
        3: {'name': 'Visites', 'clients': clients.filter(pipeline_stage=3)},
        4: {'name': 'Négociation', 'clients': clients.filter(pipeline_stage=4)},
        5: {'name': 'Signé / Conclu', 'clients': clients.filter(pipeline_stage=5)},
    }
    
    context = {
        'stages': stages,
    }
    return render(request, 'agency/agency_pipeline.html', context)


@agency_saas_required
@require_POST
def agency_update_pipeline_stage(request):
    """
    AJAX endpoint to update client stage on Kanban drag/drop.
    """
    agency = request.user
    client_id = request.POST.get('client_id')
    new_stage = request.POST.get('stage')
    
    try:
        client = get_object_or_404(AgencyClient, id=client_id, agency=agency)
        client.pipeline_stage = int(new_stage)
        # Automatically update status based on pipeline stage
        if client.pipeline_stage == 5:
            client.status = AgencyClient.ClientStatus.ACTIVE
        client.save()
        return JsonResponse({'status': 'success', 'client': client.full_name, 'new_stage': client.pipeline_stage})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@agency_saas_required
def agency_leases(request):
    """
    Lease contract view & creator wizard.
    """
    agency = request.user
    leases = Lease.objects.filter(landlord=agency)
    
    # Properties belonging to this agency
    properties = Property.objects.filter(owner=agency)
    
    # Only fetch tenants that belong to this agency
    tenants = User.objects.filter(parent_agency=agency, role='TENANT')
    
    # Contract templates belonging to this agency
    contract_templates = ContractTemplate.objects.filter(agency=agency)
    
    if request.method == 'POST':
        property_id = request.POST.get('property')
        tenant_id = request.POST.get('tenant')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        rent_amount = request.POST.get('rent_amount')
        deposit_amount = request.POST.get('deposit_amount', 0)
        custom_terms = request.POST.get('custom_terms', '')
        custom_header = request.POST.get('custom_header', '')
        payment_due_day = request.POST.get('payment_due_day', 5)
        template_id = request.POST.get('template')
        
        prop = get_object_or_404(Property, id=property_id, owner=agency)
        tenant_user = get_object_or_404(User, id=tenant_id)
        
        # Load template if selected
        selected_template = None
        if template_id:
            selected_template = get_object_or_404(ContractTemplate, id=template_id, agency=agency)
        
        if prop and tenant_user and start_date and rent_amount:
            lease = Lease.objects.create(
                property=prop,
                tenant=tenant_user,
                landlord=agency,
                start_date=start_date,
                end_date=end_date if end_date else None,
                rent_amount=rent_amount,
                deposit_amount=deposit_amount if deposit_amount else 0,
                custom_contract_terms=custom_terms,
                custom_header_text=custom_header,
                payment_due_day=int(payment_due_day) if payment_due_day else 5,
                template=selected_template,
                status=Lease.StatusEnum.ACTIVE
            )
            
            # Generate the first unpaid RentPayment for this new lease
            # For the current month
            today = timezone.now().date()
            RentPayment.objects.create(
                lease=lease,
                period_start=today.replace(day=1),
                period_end=today, # or end of month
                amount_due=lease.rent_amount,
                status=RentPayment.StatusEnum.UNPAID
            )
            
            messages.success(request, f"Contrat de bail créé pour {tenant_user.get_full_name()} avec succès.")
            return redirect('agency_leases')
        else:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            
    context = {
        'leases': leases,
        'properties': properties,
        'tenants': tenants,
        'contract_templates': contract_templates,
        'statuses': Lease.StatusEnum.choices,
    }
    return render(request, 'agency/agency_leases.html', context)
@agency_saas_required
def agency_templates(request):
    """
    Gestion des modèles de contrats de bail personnalisables pour l'agence.
    """
    agency = request.user
    templates = ContractTemplate.objects.filter(agency=agency)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            title = request.POST.get('title')
            content = request.POST.get('content')
            if title and content:
                ContractTemplate.objects.create(
                    agency=agency,
                    title=title,
                    content=content
                )
                messages.success(request, "Modèle de contrat créé avec succès.")
            else:
                messages.error(request, "Veuillez remplir tous les champs.")
                
        elif action == 'edit':
            template_id = request.POST.get('template_id')
            title = request.POST.get('title')
            content = request.POST.get('content')
            template = get_object_or_404(ContractTemplate, id=template_id, agency=agency)
            if title and content:
                template.title = title
                template.content = content
                template.save()
                messages.success(request, "Modèle de contrat mis à jour.")
            else:
                messages.error(request, "Veuillez remplir tous les champs.")
                
        elif action == 'delete':
            template_id = request.POST.get('template_id')
            template = get_object_or_404(ContractTemplate, id=template_id, agency=agency)
            template.delete()
            messages.success(request, "Modèle de contrat supprimé.")
            
        return redirect('agency_templates')
        
    return render(request, 'agency/agency_templates.html', {'templates': templates})


@agency_saas_required
def agency_payments(request):
    """
    Rent payments ledger & payment collection helper with Advanced Accounting.
    """
    agency = request.user
    
    # Advanced Filtering
    status_filter = request.GET.get('status', '')
    property_filter = request.GET.get('property', '')
    tenant_filter = request.GET.get('tenant', '')
    
    payments_qs = RentPayment.objects.filter(lease__landlord=agency)
    
    if status_filter:
        payments_qs = payments_qs.filter(status=status_filter)
    if property_filter:
        payments_qs = payments_qs.filter(lease__property_id=property_filter)
    if tenant_filter:
        payments_qs = payments_qs.filter(lease__tenant_id=tenant_filter)
        
    payments = list(payments_qs.order_by('-period_start'))
    today = timezone.now().date()
    for p in payments:
        due_day = p.lease.payment_due_day
        try:
            due_date = p.period_start.replace(day=due_day)
        except ValueError:
            due_date = p.period_start.replace(day=28)
        p.is_overdue = (p.status != RentPayment.StatusEnum.PAID) and (today > due_date)
    
    # Advanced Accounting Totals
    totals = payments_qs.aggregate(
        due=Sum('amount_due'),
        paid=Sum('amount_paid')
    )
    total_due = totals['due'] or 0
    total_paid = totals['paid'] or 0
    total_outstanding = total_due - total_paid
    
    # Active leases list for recording payments
    active_leases = Lease.objects.filter(landlord=agency, status=Lease.StatusEnum.ACTIVE)
    
    # Distinct properties and tenants for filters
    filter_properties = Property.objects.filter(leases__landlord=agency).distinct()
    filter_tenants = User.objects.filter(tenant_leases__landlord=agency).distinct()
    
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        amount_paid = request.POST.get('amount_paid')
        date_paid = request.POST.get('date_paid')
        payment_method = request.POST.get('payment_method', 'ESPECES')
        receipt_header = request.POST.get('receipt_header', '')
        receipt_footer = request.POST.get('receipt_footer', '')
        receipt_logo = request.FILES.get('receipt_logo')
        
        payment = get_object_or_404(RentPayment, id=payment_id, lease__landlord=agency)
        
        if payment and amount_paid:
            amt = float(amount_paid)
            payment.amount_paid = amt
            payment.date_paid = date_paid if date_paid else timezone.now().date()
            payment.payment_method = payment_method
            payment.receipt_header = receipt_header
            payment.receipt_footer = receipt_footer
            if receipt_logo:
                payment.receipt_logo = receipt_logo
                
            if amt >= float(payment.amount_due):
                payment.status = RentPayment.StatusEnum.PAID
            elif amt > 0:
                payment.status = RentPayment.StatusEnum.PARTIAL
            else:
                payment.status = RentPayment.StatusEnum.UNPAID
                
            payment.save()
            messages.success(request, f"Paiement de {amt} FCFA enregistré avec succès pour {payment.lease.tenant.get_full_name()}.")
            return redirect('agency_payments')
            
    context = {
        'payments': payments,
        'active_leases': active_leases,
        'statuses': RentPayment.StatusEnum.choices,
        'filter_properties': filter_properties,
        'filter_tenants': filter_tenants,
        'status_filter': status_filter,
        'property_filter': property_filter,
        'tenant_filter': tenant_filter,
        'total_due': total_due,
        'total_paid': total_paid,
        'total_outstanding': total_outstanding,
    }
    return render(request, 'agency/agency_payments.html', context)


@agency_saas_required
def agency_receipt(request, payment_id):
    """
    Render a high-end, responsive glassmorphic print page representing the rent receipt.
    Allows easy print to PDF via browser.
    """
    agency = request.user
    payment = get_object_or_404(RentPayment, id=payment_id, lease__landlord=agency)
    
    context = {
        'payment': payment,
        'agency': agency,
        'today': timezone.now().date(),
    }
    return render(request, 'agency/agency_receipt.html', context)


@agency_saas_required
def agency_properties(request):
    """
    Manage list of properties currently linked to the agency.
    """
    agency = request.user
    properties = Property.objects.filter(owner=agency).order_by('-created_at')
    
    context = {
        'properties': properties,
    }
    return render(request, 'agency/agency_properties.html', context)


@agency_saas_required
def agency_property_create(request):
    """
    SaaS Property Creation directly from agence.logertogo.com dashboard.
    No need to return to the main site.
    """
    from logersn.forms import PropertyForm
    from logersn.constants import TOGO_NEIGHBORHOODS
    from logersn.models import PropertyImage

    agency = request.user
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                p = form.save(commit=False)
                p.owner = agency
                
                # Check publication toggle
                make_public = request.POST.get('make_public') == 'on'
                if make_public:
                    p.publication_requested = True
                    p.is_published = True
                    p.is_authorized_by_admin = True
                else:
                    p.publication_requested = False
                    p.is_published = False
                
                p.save()
                
                # Multi-image upload
                images = request.FILES.getlist('images')
                for i, img in enumerate(images):
                    PropertyImage.objects.create(property=p, image_url=img, is_primary=(i == 0))
                
                if make_public:
                    messages.success(request, f"Le bien '{p.title}' a été créé. La demande de publication sur le site d'annonces est en attente d'autorisation.")
                else:
                    messages.success(request, f"Le bien '{p.title}' a été créé avec succès pour votre agence.")
                
                return redirect('agency_properties')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création du bien : {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = PropertyForm()

    context = {
        'form': form,
        'togo_neighborhoods': TOGO_NEIGHBORHOODS,
    }
    return render(request, 'agency/agency_property_form.html', context)


@agency_saas_required
def agency_property_edit(request, property_id):
    """
    SaaS Property Editing directly from agence.logertogo.com dashboard.
    """
    from logersn.forms import PropertyForm
    from logersn.constants import TOGO_NEIGHBORHOODS
    from logersn.models import PropertyImage

    agency = request.user
    p = get_object_or_404(Property, id=property_id, owner=agency)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=p)
        if form.is_valid():
            try:
                p = form.save(commit=False)
                
                make_public = request.POST.get('make_public') == 'on'
                if make_public:
                    if not p.is_authorized_by_admin:
                        p.publication_requested = True
                        p.is_published = False
                else:
                    p.is_published = False
                    p.publication_requested = False
                
                p.save()
                
                # Multi-image upload in edit
                images = request.FILES.getlist('images')
                if images:
                    for img in images:
                        PropertyImage.objects.create(property=p, image_url=img)
                
                messages.success(request, f"Le bien '{p.title}' a été mis à jour avec succès.")
                return redirect('agency_properties')
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification : {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = PropertyForm(instance=p)

    context = {
        'form': form,
        'property': p,
        'is_edit': True,
        'togo_neighborhoods': TOGO_NEIGHBORHOODS,
    }
    return render(request, 'agency/agency_property_form.html', context)


@agency_saas_required
def agency_property_toggle_publication(request, property_id):
    """
    Quick publication request/toggle endpoint.
    """
    agency = request.user
    p = get_object_or_404(Property, id=property_id, owner=agency)
    
    if p.is_published:
        # Easy withdraw
        p.is_published = False
        p.publication_requested = False
        p.save()
        messages.success(request, f"Le bien '{p.title}' a été retiré de la publication publique.")
    else:
        # Request publication
        if p.is_authorized_by_admin:
            # Already authorized previously, immediately go public
            p.is_published = True
            p.publication_requested = True
            p.save()
            messages.success(request, f"Le bien '{p.title}' est maintenant publié publiquement.")
        else:
            p.publication_requested = True
            p.is_published = False
            p.save()
            messages.success(request, f"La demande de publication publique pour le bien '{p.title}' a été envoyée. En attente de validation.")
            
    return redirect('agency_properties')


def agency_404_handler(request, exception=None):
    """
    Subdomain custom 404 Page Not Found view.
    """
    return render(request, 'agency/404.html', status=404)


def agency_500_handler(request):
    """
    Subdomain custom 500 Server Error view.
    """
    return render(request, 'agency/500.html', status=500)


@agency_saas_required
def agency_lease_agreement(request, lease_id):
    """
    Renders the official lease agreement template for printing.
    """
    agency = request.user
    lease = get_object_or_404(Lease, id=lease_id, landlord=agency)
    
    compiled_content = None
    if lease.template:
        content = lease.template.content
        # Remplacement dynamique
        content = content.replace('[LOCATAIRE]', lease.tenant.get_full_name() or lease.tenant.phone_number)
        content = content.replace('[PROPRIETAIRE]', lease.landlord.get_full_name() or lease.landlord.phone_number)
        
        company_name = getattr(lease.landlord, 'company_name', '')
        if not company_name:
            company_name = lease.landlord.get_full_name() or lease.landlord.phone_number
        content = content.replace('[AGENCE]', company_name)
        
        from django.contrib.humanize.templatetags.humanize import intcomma
        try:
            rent_formatted = f"{intcomma(int(lease.rent_amount))} FCFA"
        except Exception:
            rent_formatted = f"{lease.rent_amount} FCFA"
            
        try:
            deposit_formatted = f"{intcomma(int(lease.deposit_amount))} FCFA"
        except Exception:
            deposit_formatted = f"{lease.deposit_amount} FCFA"
            
        content = content.replace('[LOYER]', rent_formatted)
        content = content.replace('[CAUTION]', deposit_formatted)
        
        # Safe fetch for city display
        city_display = lease.property.city
        if hasattr(lease.property, 'get_city_display'):
            city_display = lease.property.get_city_display()
            
        prop_desc = f"{lease.property.title} sis à {lease.property.neighborhood} ({city_display})"
        content = content.replace('[BIEN]', prop_desc)
        content = content.replace('[DATE_DEBUT]', lease.start_date.strftime('%d/%m/%Y') if hasattr(lease.start_date, 'strftime') else str(lease.start_date))
        
        end_date_str = "Indéterminée"
        if lease.end_date:
            end_date_str = lease.end_date.strftime('%d/%m/%Y') if hasattr(lease.end_date, 'strftime') else str(lease.end_date)
        content = content.replace('[DATE_FIN]', end_date_str)
        
        compiled_content = content
        
    context = {
        'filiation': {
            'landlord': lease.landlord,
            'tenant': lease.tenant,
            'property': lease.property,
            'monthly_rent': lease.rent_amount,
            'start_date': lease.start_date,
            'end_date': lease.end_date,
            'id': lease.id,
        },
        'compiled_content': compiled_content,
        'today': timezone.now().date(),
    }
    return render(request, 'lease_agreement_pdf.html', context)


@agency_saas_required
def export_clients_csv(request):
    """
    Export clients and prospects database to CSV.
    """
    import csv
    agency = request.user
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="export_clients_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nom complet', 'Email', 'Téléphone', 'Type', 'Statut', 'Notes', 'Créé le'])
    
    clients = AgencyClient.objects.filter(agency=agency).order_by('-created_at')
    for c in clients:
        writer.writerow([
            c.full_name,
            c.email or '',
            c.phone,
            c.get_client_type_display(),
            c.get_status_display(),
            c.notes or '',
            c.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    return response


@agency_saas_required
def export_leases_csv(request):
    """
    Export all active and inactive lease contracts to CSV.
    """
    import csv
    agency = request.user
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="export_baux_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Bien', 'Locataire', 'Date début', 'Date fin', 'Loyer mensuel (FCFA)', 'Caution (FCFA)', 'Statut'])
    
    leases = Lease.objects.filter(landlord=agency).order_by('-created_at')
    for l in leases:
        writer.writerow([
            l.property.title,
            l.tenant.get_full_name() or l.tenant.phone_number,
            l.start_date.strftime('%Y-%m-%d'),
            l.end_date.strftime('%Y-%m-%d') if l.end_date else 'Indéterminée',
            float(l.rent_amount),
            float(l.deposit_amount),
            l.get_status_display()
        ])
    return response


@agency_saas_required
def export_payments_csv(request):
    """
    Export all period rents payments and accounts records to CSV.
    """
    import csv
    agency = request.user
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="export_comptabilite_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Bien', 'Locataire', 'Période du', 'Période au', 'Montant Dû (FCFA)', 'Montant Payé (FCFA)', 'Statut', 'Date de Paiement', 'Mode de Paiement'])
    
    payments = RentPayment.objects.filter(lease__landlord=agency).order_by('-period_start')
    for p in payments:
        writer.writerow([
            p.lease.property.title,
            p.lease.tenant.get_full_name() or p.lease.tenant.phone_number,
            p.period_start.strftime('%Y-%m-%d'),
            p.period_end.strftime('%Y-%m-%d'),
            float(p.amount_due),
            float(p.amount_paid),
            p.get_status_display(),
            p.date_paid.strftime('%Y-%m-%d') if p.date_paid else '',
            p.payment_method or ''
        ])
    return response


@login_required
def agency_lease_sign(request, lease_id):
    """
    Interface de signature électronique de bail.
    """
    from django.http import HttpResponseForbidden
    lease = get_object_or_404(Lease, id=lease_id)
    # Protection IDOR : seul le bailleur ou le locataire peut signer
    if request.user != lease.landlord and request.user != lease.tenant:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à signer ce bail.")
        
    user_role = 'landlord' if request.user == lease.landlord else 'tenant'
    
    if request.method == 'POST':
        otp_entered = request.POST.get('otp_code', '').strip()
        if user_role == 'landlord':
            if lease.landlord_otp and otp_entered == lease.landlord_otp:
                lease.is_signed_by_landlord = True
                lease.landlord_otp = None
                messages.success(request, "Bail signé avec succès par l'agence/bailleur !")
            else:
                messages.error(request, "Code OTP incorrect.")
        else:
            if lease.tenant_otp and otp_entered == lease.tenant_otp:
                lease.is_signed_by_tenant = True
                lease.tenant_otp = None
                messages.success(request, "Bail signé avec succès par le locataire !")
            else:
                messages.error(request, "Code OTP incorrect.")
                
        # Si les deux ont signé, activer le bail
        if lease.is_signed_by_tenant and lease.is_signed_by_landlord:
            lease.status = Lease.StatusEnum.ACTIVE
            lease.signed_at = timezone.now()
            messages.success(request, "Félicitations ! Le bail est désormais entièrement signé et ACTIF.")
            
        lease.save()
        return redirect('agency_leases')
        
    context = {
        'lease': lease,
        'user_role': user_role,
    }
    return render(request, 'agency/signer.html', context)


@login_required
def agency_lease_otp(request, lease_id):
    """
    Génération et simulation d'envoi d'OTP de signature par SMS.
    """
    import random
    lease = get_object_or_404(Lease, id=lease_id)
    if request.user != lease.landlord and request.user != lease.tenant:
        return JsonResponse({'success': False, 'message': 'Non autorisé.'}, status=403)
        
    otp = f"{random.randint(100000, 999999)}"
    
    if request.user == lease.landlord:
        lease.landlord_otp = otp
        recipient = lease.landlord.get_full_name() or lease.landlord.phone_number
    else:
        lease.tenant_otp = otp
        recipient = lease.tenant.get_full_name() or lease.tenant.phone_number
        
    lease.save()
    
    # Simulation d'envoi SMS
    msg = f"[SIMULATION SECURE SIGN LOGER TOGO] OTP envoyé par SMS à {recipient} : {otp}"
    print(msg)
    
    return JsonResponse({
        'success': True, 
        'otp': otp, 
        'message': f"OTP généré avec succès ! Le code est : {otp} (Simulation d'envoi de SMS sur {recipient})"
    })


@agency_saas_required
def agency_financial_analysis(request):
    """
    Dashboard d'Analyse Financière Premium pour l'agence.
    """
    agency = request.user
    payments = RentPayment.objects.filter(lease__landlord=agency)
    
    # 1. KPIs avancés
    total_due = payments.aggregate(total=Sum('amount_due'))['total'] or 0
    total_paid = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    total_outstanding = payments.filter(status=RentPayment.StatusEnum.UNPAID).aggregate(total=Sum('amount_due'))['total'] or 0
    
    # Taux de recouvrement
    recovery_rate = 0
    if total_due > 0:
        recovery_rate = round((total_paid / total_due) * 100, 1)
        
    # Modes de paiement
    payment_methods_stats = payments.filter(status=RentPayment.StatusEnum.PAID).values('payment_method').annotate(count=Count('id'), total=Sum('amount_paid'))
    payment_methods_data = []
    for stat in payment_methods_stats:
        payment_methods_data.append({
            'label': stat['payment_method'] or 'Non spécifié',
            'total': float(stat['total'] or 0),
            'count': stat['count']
        })
        
    # Évolution mensuelle
    months_labels = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    monthly_expected = [0] * 12
    monthly_collected = [0] * 12
    
    for p in payments:
        month_idx = p.period_start.month - 1
        monthly_expected[month_idx] += float(p.amount_due)
        if p.status == RentPayment.StatusEnum.PAID:
            monthly_collected[month_idx] += float(p.amount_paid)
            
    # Répartition par catégorie de bien
    category_revenue = {'RENT': 0, 'FURNISHED': 0}
    category_payments = payments.filter(status=RentPayment.StatusEnum.PAID)
    for p in category_payments:
        cat = p.lease.property.listing_category
        if cat in category_revenue:
            category_revenue[cat] += float(p.amount_paid)
            
    context = {
        'total_due': total_due,
        'total_paid': total_paid,
        'total_outstanding': total_outstanding,
        'recovery_rate': recovery_rate,
        'payment_methods_data': payment_methods_data,
        'months_labels': months_labels,
        'monthly_expected': monthly_expected,
        'monthly_collected': monthly_collected,
        'category_revenue': category_revenue,
    }
    return render(request, 'agency/financial_analysis.html', context)


@agency_saas_required
def agency_inventories(request):
    """
    Liste des états des lieux effectués.
    """
    agency = request.user
    inventories = PropertyInventory.objects.filter(lease__landlord=agency).order_by('-inventory_date')
    return render(request, 'agency/agency_inventories.html', {'inventories': inventories})


@agency_saas_required
def agency_inventory_create(request, lease_id):
    """
    Création d'un état des lieux pour un bail donné.
    """
    import json
    lease = get_object_or_404(Lease, id=lease_id, landlord=request.user)
    
    if request.method == 'POST':
        try:
            inv_type = request.POST.get('inventory_type', 'IN')
            inv_date = request.POST.get('inventory_date', timezone.now().date())
            gen_cond = request.POST.get('general_condition', 'GOOD')
            
            # Récupérer les détails JSON structurés
            details = request.POST.get('details_json', '{}')
            
            # Récupérer les signatures Base64
            sig_tenant = request.POST.get('signature_tenant', '')
            sig_agent = request.POST.get('signature_agent', '')
            
            inventory = PropertyInventory.objects.create(
                lease=lease,
                inventory_type=inv_type,
                inventory_date=inv_date,
                general_condition=gen_cond,
                details_json=details,
                signature_tenant=sig_tenant,
                signature_agent=sig_agent
            )
            messages.success(request, f"État des lieux d'élire ({inventory.get_inventory_type_display()}) enregistré avec succès !")
            return redirect('agency_inventories')
        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement de l'état des lieux : {e}")
            
    # Structure par défaut pour accélérer la saisie
    default_structure = [
        {"room": "Salon / Séjour", "components": [
            {"name": "Sols / Carrelages", "condition": "GOOD", "comment": ""},
            {"name": "Murs / Peinture", "condition": "GOOD", "comment": ""},
            {"name": "Plafonds / Éclairage", "condition": "GOOD", "comment": ""},
            {"name": "Fenêtres / Vitrages", "condition": "GOOD", "comment": ""}
        ]},
        {"room": "Cuisine", "components": [
            {"name": "Évier / Plomberie", "condition": "GOOD", "comment": ""},
            {"name": "Murs / Peinture", "condition": "GOOD", "comment": ""},
            {"name": "Prises électriques", "condition": "GOOD", "comment": ""},
            {"name": "Placards / Rangements", "condition": "GOOD", "comment": ""}
        ]},
        {"room": "Chambre Principale", "components": [
            {"name": "Sols / Carrelages", "condition": "GOOD", "comment": ""},
            {"name": "Murs / Peinture", "condition": "GOOD", "comment": ""},
            {"name": "Climatisation / Brasseur", "condition": "GOOD", "comment": ""},
            {"name": "Portes / Serrures", "condition": "GOOD", "comment": ""}
        ]},
        {"room": "Salle de bain / Douche", "components": [
            {"name": "W.C. / Chasse d'eau", "condition": "GOOD", "comment": ""},
            {"name": "Douche / Robinetterie", "condition": "GOOD", "comment": ""},
            {"name": "Carrelage mural", "condition": "GOOD", "comment": ""},
            {"name": "Miroir / Vasque", "condition": "GOOD", "comment": ""}
        ]}
    ]
    
    context = {
        'lease': lease,
        'default_structure_json': json.dumps(default_structure),
    }
    return render(request, 'agency/agency_inventory_form.html', context)


@agency_saas_required
def agency_inventory_detail(request, inventory_id):
    """
    Rapport d'état des lieux A4 formaté pour impression.
    """
    import json
    inventory = get_object_or_404(PropertyInventory, id=inventory_id, lease__landlord=request.user)
    
    try:
        details = json.loads(inventory.details_json)
    except Exception:
        details = []
        
    context = {
        'inventory': inventory,
        'details': details,
    }
    return render(request, 'agency/agency_inventory_detail.html', context)


