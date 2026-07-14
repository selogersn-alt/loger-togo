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
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime

from django.contrib.auth import get_user_model, authenticate, login, logout
from .models import Lease, RentPayment, AgencyClient, MaintenanceRequest, ContractTemplate, PropertyInventory
from logersn.models import Property, PropertyApplication, VisitRequest, Reservation

User = get_user_model()

def agency_saas_required(view_func):
    """
    Decorator to ensure user is logged in, has the AGENCY role, and has an active SaaS subscription.
    Otherwise redirects to the agency login or promo page. Supports sub-agents (AGENT with parent_agency).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            next_url = request.build_absolute_uri()
            return redirect(f"{reverse('agency_login')}?next={next_url}")
            
        user = request.user
        is_allowed = False
        
        if user.role == 'AGENCY' and user.is_saas_active:
            is_allowed = True
        elif user.role == 'AGENT' and user.parent_agency and user.parent_agency.role == 'AGENCY' and user.parent_agency.is_saas_active:
            is_allowed = True
            
        if not is_allowed:
            # Redirect to agency landing/promo page
            return redirect('agency_promo')
            
        # Delegate context: Swap request.user with parent if it is a sub-agent
        if user.role == 'AGENT' and user.parent_agency:
            request.actual_user = user
            request.user = user.parent_agency
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def agency_login(request):
    """
    Premium login view for the agency subdomain.
    Only allows users with the AGENCY role.
    """
    if request.user.is_authenticated:
        if request.user.role == 'AGENCY' and request.user.is_saas_active:
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
                if user.role != 'AGENCY':
                    messages.error(request, "Accès refusé : ce compte n'est pas un profil d'Agence Immobilière.")
                else:
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
    Forces role as AGENCY.
    """
    if request.user.is_authenticated:
        if request.user.role == 'AGENCY' and request.user.is_saas_active:
            return redirect('agency_dashboard')
        return redirect('agency_promo')
        
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        role = User.RoleEnum.AGENCY # Force AGENCY role
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


def log_employee_action(request, action_type, description):
    """
    Log an action made by the currently logged-in negotiator / employee agent of the agency.
    """
    if hasattr(request, 'actual_user'):
        employee = request.actual_user
        parent = request.user
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            
        try:
            from management.models import EmployeeActionLog
            EmployeeActionLog.objects.create(
                hotel=parent,
                employee=employee,
                action_type=action_type,
                description=description,
                ip_address=ip
            )
        except Exception:
            pass


def check_employee_absences(manager, is_hotel=False):
    """
    Check today's employee schedules for a manager (hotel or agency).
    If an employee scheduled to work today has not clocked in and is more than 30 minutes late,
    we create an EmployeeAttendance record marked ABSENT and send a notification e-mail.
    """
    from django.utils import timezone
    import datetime
    from management.models import EmployeeSchedule, EmployeeAttendance
    from users.models import User
    from logertogo.emails import send_employee_absence_notification
    
    today = timezone.now().date()
    now_dt = timezone.now()
    day_of_week = today.isoweekday() # 1-7
    
    if is_hotel:
        staff = User.objects.filter(parent_hotel=manager, role='AGENT')
    else:
        staff = User.objects.filter(parent_agency=manager, role='AGENT')
        
    for employee in staff:
        schedule = EmployeeSchedule.objects.filter(employee=employee, day_of_week=day_of_week).first()
        if schedule:
            sched_start = timezone.make_aware(datetime.datetime.combine(today, schedule.start_time))
            if now_dt > (sched_start + datetime.timedelta(minutes=30)):
                attendance, created = EmployeeAttendance.objects.get_or_create(
                    employee=employee,
                    hotel=manager,
                    date=today,
                    defaults={'status': 'ABSENT'}
                )
                
                if not attendance.clock_in and attendance.status != 'ABSENT':
                    attendance.status = 'ABSENT'
                    attendance.notes = "Alerte Absence automatique (retard > 30 minutes)."
                    attendance.save()
                    
                if not attendance.clock_in and attendance.status == 'ABSENT' and (not attendance.notes or "Email envoyé" not in attendance.notes):
                    try:
                        send_employee_absence_notification(manager, employee, schedule.start_time)
                        attendance.notes = (attendance.notes or "") + " [Email envoyé]"
                        attendance.save()
                        
                        from management.models import EmployeeActionLog
                        EmployeeActionLog.objects.create(
                            hotel=manager,
                            employee=employee,
                            action_type="ABSENCE_DETECTED",
                            description=f"Absence constatée automatiquement : n'a pas pointé à son poste prévu à {schedule.start_time.strftime('%H:%M')}."
                        )
                    except Exception:
                        pass


@agency_saas_required
def agency_dashboard(request):
    """
    Main SaaS Dashboard for the agency with Advanced Statistics & Charts.
    """
    from .models import EmployeeSchedule, EmployeeAttendance, EmployeeTask
    from datetime import date
    agency = request.user
    today = timezone.now().date()
    
    # 1. Core KPIs
    total_clients = AgencyClient.objects.filter(agency=agency).count()
    total_properties = Property.objects.filter(owner=agency).count()
    my_leases = Lease.objects.filter(landlord=agency)
    total_leases = my_leases.count()
    active_leases_count = my_leases.filter(status=Lease.StatusEnum.ACTIVE).count()
    
    # Occupancy Rate
    occupancy_rate = 0
    if total_properties > 0:
        occupied_count = my_leases.filter(status=Lease.StatusEnum.ACTIVE).values('property').distinct().count()
        occupancy_rate = round((occupied_count / total_properties) * 100, 1)
    
    # Revenue
    payments = RentPayment.objects.filter(lease__landlord=agency)
    total_revenue = payments.filter(status=RentPayment.StatusEnum.PAID).aggregate(total=Sum('amount_paid'))['total'] or 0
    total_unpaid = payments.filter(status=RentPayment.StatusEnum.UNPAID).aggregate(total=Sum('amount_due'))['total'] or 0
    
    # Recent clients & payments
    recent_clients = AgencyClient.objects.filter(agency=agency).order_by('-created_at')[:5]
    recent_payments = list(payments.order_by('-period_start')[:5])
    for p in recent_payments:
        due_day = p.lease.payment_due_day
        try:
            due_date = p.period_start.replace(day=due_day)
        except ValueError:
            due_date = p.period_start.replace(day=28)
        p.is_overdue = (p.status != RentPayment.StatusEnum.PAID) and (today > due_date)
    
    # Pipeline counts
    pipeline_stats = AgencyClient.objects.filter(agency=agency).values('pipeline_stage').annotate(count=Count('id'))
    pipeline_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for stat in pipeline_stats:
        stage = stat['pipeline_stage']
        if stage in pipeline_counts:
            pipeline_counts[stage] = stat['count']
    
    # --- CHART 1: Rolling 12 months revenue & unpaid ---
    import calendar
    rolling_labels = []
    rolling_revenue = []
    rolling_unpaid = []
    for i in range(11, -1, -1):
        if today.month - i <= 0:
            m = today.month - i + 12
            y = today.year - 1
        else:
            m = today.month - i
            y = today.year
        label = f"{calendar.month_abbr[m]} {str(y)[2:]}"
        rolling_labels.append(label)
        paid = payments.filter(
            status=RentPayment.StatusEnum.PAID,
            date_paid__year=y,
            date_paid__month=m
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        unpaid = payments.filter(
            status=RentPayment.StatusEnum.UNPAID,
            period_start__year=y,
            period_start__month=m
        ).aggregate(total=Sum('amount_due'))['total'] or 0
        rolling_revenue.append(float(paid))
        rolling_unpaid.append(float(unpaid))
    
    # --- CHART 2: Property category breakdown ---
    categories_stats = Property.objects.filter(owner=agency).values('listing_category').annotate(count=Count('id'))
    categories_data = {'RENT': 0, 'SALE': 0, 'FURNISHED': 0}
    for item in categories_stats:
        cat = item['listing_category']
        if cat in categories_data:
            categories_data[cat] = item['count']
    
    # --- CHART 3: Payment status breakdown (for current year) ---
    paid_count = payments.filter(status=RentPayment.StatusEnum.PAID).count()
    unpaid_count = payments.filter(status=RentPayment.StatusEnum.UNPAID).count()
    partial_count = payments.filter(status=RentPayment.StatusEnum.PARTIAL).count()
    
    # --- CHART 4: Top 5 tenants by revenue ---
    from django.db.models import Sum
    top_tenants = payments.filter(status=RentPayment.StatusEnum.PAID)\
        .values('lease__tenant__first_name', 'lease__tenant__last_name', 'lease__tenant__phone_number')\
        .annotate(total_paid=Sum('amount_paid'))\
        .order_by('-total_paid')[:5]
    top_tenant_labels = []
    top_tenant_values = []
    for t in top_tenants:
        name = f"{t['lease__tenant__first_name'] or ''} {t['lease__tenant__last_name'] or ''}".strip()
        if not name:
            name = t['lease__tenant__phone_number'] or '—'
        top_tenant_labels.append(name[:18])
        top_tenant_values.append(float(t['total_paid']))
    
    # Legacy months_labels for backward compat
    months_labels = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    monthly_data = [0] * 12
    for p in payments.filter(status=RentPayment.StatusEnum.PAID, date_paid__isnull=False):
        monthly_data[p.date_paid.month - 1] += float(p.amount_paid)

    # Staff Attendance & Tasks Context
    my_attendance = None
    my_tasks = None
    live_staff = None
    pending_tasks = None
    action_logs = None
    
    if hasattr(request, 'actual_user'):
        # Logged in as receptionist / agent
        my_attendance = EmployeeAttendance.objects.filter(employee=request.actual_user, date=today).first()
        my_tasks = EmployeeTask.objects.filter(employee=request.actual_user, status='PENDING').order_by('due_date')
    else:
        # Logged in as agency gérant / owner
        # Real-time proactive absence check
        check_employee_absences(agency, is_hotel=False)
        
        live_staff = EmployeeAttendance.objects.filter(hotel=agency, date=today).select_related('employee')
        pending_tasks = EmployeeTask.objects.filter(hotel=agency, status='PENDING').select_related('employee')[:5]
        
        from management.models import EmployeeActionLog
        action_logs = EmployeeActionLog.objects.filter(hotel=agency).select_related('employee')[:15]

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
        # Charts
        'months_labels': months_labels,
        'monthly_data': monthly_data,
        'rolling_labels': rolling_labels,
        'rolling_revenue': rolling_revenue,
        'rolling_unpaid': rolling_unpaid,
        'categories_data': categories_data,
        'paid_count': paid_count,
        'unpaid_count': unpaid_count,
        'partial_count': partial_count,
        'top_tenant_labels': top_tenant_labels,
        'top_tenant_values': top_tenant_values,
        # Staff
        'my_attendance': my_attendance,
        'my_tasks': my_tasks,
        'live_staff': live_staff,
        'pending_tasks': pending_tasks,
        'action_logs': action_logs,
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
    
    # Contract templates belonging to this agency or global templates
    contract_templates = ContractTemplate.objects.filter(Q(agency=agency) | Q(agency__isnull=True))
    
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
            selected_template = get_object_or_404(ContractTemplate, Q(id=template_id) & (Q(agency=agency) | Q(agency__isnull=True)))
        
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
    templates = ContractTemplate.objects.filter(Q(agency=agency) | Q(agency__isnull=True))
    
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
def agency_profile(request):
    """
    Agency profile management: logo, full coordinates, RCCM, NIF, etc.
    These fields are printed on official documents (receipts, contracts).
    """
    agency = request.user
    
    if request.method == 'POST':
        # Text fields
        agency.company_name = request.POST.get('company_name', agency.company_name)
        agency.first_name = request.POST.get('first_name', agency.first_name)
        agency.last_name = request.POST.get('last_name', agency.last_name)
        agency.bio = request.POST.get('bio', agency.bio)
        agency.agency_tagline = request.POST.get('agency_tagline', '')
        agency.agency_address = request.POST.get('agency_address', '')
        agency.agency_city = request.POST.get('agency_city', '')
        agency.agency_neighborhood = request.POST.get('agency_neighborhood', '')
        agency.agency_phone_mobile = request.POST.get('agency_phone_mobile', '')
        agency.agency_phone_landline = request.POST.get('agency_phone_landline', '')
        agency.agency_email = request.POST.get('agency_email', '') or None
        agency.agency_website = request.POST.get('agency_website', '') or None
        agency.agency_rccm = request.POST.get('agency_rccm', '')
        agency.agency_nif = request.POST.get('agency_nif', '')
        
        # GPS Coordinates
        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')
        if lat and lng:
            try:
                agency.agency_latitude = float(lat)
                agency.agency_longitude = float(lng)
            except ValueError:
                pass
        
        # File: logo
        if 'profile_picture' in request.FILES:
            agency.profile_picture = request.FILES['profile_picture']
        
        agency.save()
        messages.success(request, "Profil de l'agence mis à jour avec succès. Vos documents reflèteront ces nouvelles informations.")
        return redirect('agency_profile')
    
    from logersn.constants import CITY_CHOICES, TOGO_NEIGHBORHOODS
    context = {
        'city_choices': CITY_CHOICES,
        'togo_neighborhoods': TOGO_NEIGHBORHOODS,
    }
    return render(request, 'agency/agency_profile.html', context)


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
def agency_receipt_pdf(request, payment_id):
    """
    Server-side PDF generation for a rent receipt using xhtml2pdf.
    Returns a proper PDF download (no browser print dialog).
    """
    from io import BytesIO
    from xhtml2pdf import pisa
    from django.template.loader import render_to_string

    agency = request.user
    payment = get_object_or_404(RentPayment, id=payment_id, lease__landlord=agency)

    context = {
        'payment': payment,
        'agency': agency,
        'today': timezone.now().date(),
        'request': request,
    }

    html_string = render_to_string('agency/agency_receipt_pdf.html', context, request=request)

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=buffer, encoding='UTF-8')

    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)

    buffer.seek(0)
    filename = f"Quittance-{payment.lease.tenant.get_full_name().replace(' ', '_')}-{payment.period_start.strftime('%m%Y')}.pdf"
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@agency_saas_required
def agency_lease_pdf(request, lease_id):
    """
    Server-side PDF generation for a lease agreement using xhtml2pdf.
    Uses the compiled template content.
    """
    from io import BytesIO
    from xhtml2pdf import pisa
    from django.template.loader import render_to_string
    from management.models import ContractTemplate

    agency = request.user
    filiation = get_object_or_404(Lease, id=lease_id, landlord=agency)

    # Get compiled content (same logic as agency_lease_agreement)
    template_id = request.GET.get('template')
    compiled_content = None

    if template_id:
        try:
            template = ContractTemplate.objects.get(id=template_id)
        except ContractTemplate.DoesNotExist:
            template = None
    else:
        template = ContractTemplate.objects.filter(agency=agency).first() or \
                   ContractTemplate.objects.filter(agency=None).first()

    if template:
        content = template.content
        replacements = {
            '[NOM_BAILLEUR]': agency.company_name or agency.get_full_name(),
            '[NOM_COMPLET_CLIENT]': filiation.tenant.get_full_name(),
            '[NATIONALITE_CLIENT]': filiation.tenant.document_country or 'Togolaise',
            '[NUMERO_CARTE_CLIENT]': filiation.tenant.cni_number or '___________',
            '[TYPE_DE_BIEN]': filiation.property.get_property_type_display() if hasattr(filiation.property, 'get_property_type_display') else 'Appartement',
            '[DETAILS_DE_BIEN]': f"{filiation.property.title} — {filiation.property.neighborhood or ''}, {filiation.property.get_city_display() if hasattr(filiation.property, 'get_city_display') else ''}",
            '[TYPE_D_USAGE]': 'Habitation',
            '[PRIX_DU_BIEN]': f"{int(filiation.monthly_rent):,} FCFA".replace(',', ' '),
            '[CAUTION]': f"{int(filiation.deposit_amount):,} FCFA".replace(',', ' ') if filiation.deposit_amount else 'Néant',
            '[DATE_DEBUT_CONTRAT]': filiation.start_date.strftime('%d/%m/%Y') if filiation.start_date else '—',
            '[DATE_FIN_CONTRAT]': filiation.end_date.strftime('%d/%m/%Y') if filiation.end_date else 'Indéterminée',
            '[DATE_D_ETABLISSEMENT]': timezone.now().strftime('%d/%m/%Y'),
            '[SIGNATURE_BAILLEUR]': '',
            '[SIGNATURE_LOCATAIRE]': '',
        }
        for key, val in replacements.items():
            content = content.replace(key, str(val))
        compiled_content = content

    context = {
        'filiation': filiation,
        'compiled_content': compiled_content,
        'today': timezone.now().date(),
        'request': request,
    }

    html_string = render_to_string('lease_agreement_pdf.html', context, request=request)

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=buffer, encoding='UTF-8')

    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)

    buffer.seek(0)
    filename = f"Contrat-{filiation.tenant.get_full_name().replace(' ', '_')}-{filiation.start_date.strftime('%m%Y') if filiation.start_date else 'ND'}.pdf"
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


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
                
                # Check portal visibility
                visible_on_portal = request.POST.get('visible_on_portal') == 'on'
                p.visible_on_portal = visible_on_portal
                
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
                
                visible_on_portal = request.POST.get('visible_on_portal') == 'on'
                p.visible_on_portal = visible_on_portal
                
                make_public = request.POST.get('make_public') == 'on'
                if make_public:
                    if not p.is_authorized_by_admin:
                        p.publication_requested = True
                        p.is_published = False
                else:
                    p.is_published = False
                    p.publication_requested = False
                
                p.save()
                
                # Image deletion handling
                delete_ids = request.POST.getlist('delete_images')
                if delete_ids:
                    PropertyImage.objects.filter(id__in=delete_ids, property=p).delete()
                    # Ensure primary image if necessary
                    remaining = p.images.all()
                    if remaining.exists() and not remaining.filter(is_primary=True).exists():
                        first_img = remaining.first()
                        first_img.is_primary = True
                        first_img.save()
                
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
        # Remplacement dynamique (Contexte Togolais)
        
        # Bailleur
        company_name = getattr(lease.landlord, 'company_name', '')
        nom_bailleur = company_name if company_name else (lease.landlord.get_full_name() or lease.landlord.phone_number)
        content = content.replace('[NOM_BAILLEUR]', nom_bailleur)
        content = content.replace('[PROPRIETAIRE]', nom_bailleur) # Fallback pour compatibilité
        content = content.replace('[AGENCE]', nom_bailleur) # Fallback
        
        # Locataire
        nom_client = lease.tenant.get_full_name() or lease.tenant.phone_number
        content = content.replace('[NOM_COMPLET_CLIENT]', nom_client)
        content = content.replace('[LOCATAIRE]', nom_client) # Fallback
        
        # Nationalité et CNI (User model)
        nationalite = lease.tenant.document_country or 'Togo'
        cni_number = lease.tenant.cni_number or 'Non renseigné'
        content = content.replace('[NATIONALITE_CLIENT]', nationalite)
        content = content.replace('[NUMERO_CARTE_CLIENT]', cni_number)
        
        # Bien Immobilier
        type_bien = lease.property.get_property_type_display() if hasattr(lease.property, 'get_property_type_display') else str(lease.property.property_type)
        content = content.replace('[TYPE_DE_BIEN]', type_bien)
        
        type_usage = 'Habitation' # Par défaut
        content = content.replace('[TYPE_D_USAGE]', type_usage)
        
        city_display = lease.property.city
        if hasattr(lease.property, 'get_city_display'):
            city_display = lease.property.get_city_display()
        
        surface = f", {lease.property.surface} m²" if getattr(lease.property, 'surface', None) else ""
        bedrooms = f", {lease.property.bedrooms} chambres" if getattr(lease.property, 'bedrooms', None) else ""
        details_bien = f"{lease.property.title} sis à {lease.property.neighborhood} ({city_display}){bedrooms}{surface}"
        content = content.replace('[DETAILS_DE_BIEN]', details_bien)
        content = content.replace('[BIEN]', details_bien) # Fallback
        
        # Finances
        from django.contrib.humanize.templatetags.humanize import intcomma
        try:
            prix_bien = f"{intcomma(int(lease.rent_amount))} FCFA"
        except Exception:
            prix_bien = f"{lease.rent_amount} FCFA"
            
        try:
            deposit_formatted = f"{intcomma(int(lease.deposit_amount))} FCFA"
        except Exception:
            deposit_formatted = f"{lease.deposit_amount} FCFA"
            
        content = content.replace('[PRIX_DU_BIEN]', prix_bien)
        content = content.replace('[LOYER]', prix_bien) # Fallback
        content = content.replace('[CAUTION]', deposit_formatted)
        
        # Dates
        date_debut = lease.start_date.strftime('%d/%m/%Y') if hasattr(lease.start_date, 'strftime') else str(lease.start_date)
        content = content.replace('[DATE_DEBUT_CONTRAT]', date_debut)
        content = content.replace('[DATE_DEBUT]', date_debut) # Fallback
        
        date_fin = "Indéterminée"
        if lease.end_date:
            date_fin = lease.end_date.strftime('%d/%m/%Y') if hasattr(lease.end_date, 'strftime') else str(lease.end_date)
        content = content.replace('[DATE_FIN_CONTRAT]', date_fin)
        content = content.replace('[DATE_FIN]', date_fin) # Fallback
        
        date_etablissement = timezone.now().strftime('%d/%m/%Y')
        content = content.replace('[DATE_D_ETABLISSEMENT]', date_etablissement)
        
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


@login_required
def agency_inventory_detail(request, inventory_id):
    """
    Rapport d'état des lieux A4 formaté pour impression.
    Accessible par le bailleur et le locataire lié.
    """
    import json
    inventory = get_object_or_404(PropertyInventory, id=inventory_id)
    
    # Sécurité : Seul le bailleur ou le locataire du bail peut y accéder
    if request.user != inventory.lease.landlord and request.user != inventory.lease.tenant:
        messages.error(request, "Accès refusé.")
        return redirect('dashboard')
    
    try:
        details = json.loads(inventory.details_json)
    except Exception:
        details = []
        
    context = {
        'inventory': inventory,
        'details': details,
    }
    return render(request, 'agency/agency_inventory_detail.html', context)


@login_required
@agency_saas_required
def agency_sub_agents(request):
    if hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les administrateurs de l'agence peuvent gérer les collaborateurs.")
        return redirect('agency_dashboard')
        
    agency = request.user
    staff = User.objects.filter(parent_agency=agency, role='AGENT')
    staff_count = staff.count()
    
    if request.method == 'POST':
        if staff_count >= 5:
            messages.error(request, "Limite de collaborateurs atteinte. Vous ne pouvez pas ajouter plus de 5 sous-agents.")
            return redirect('agency_sub_agents')
            
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone_number')
        password = request.POST.get('password')
        email = request.POST.get('email')
        
        if first_name and last_name and phone and password:
            try:
                phone_clean = phone.replace(' ', '').replace('-', '')
                if not phone_clean.startswith('+') and len(phone_clean) == 8:
                    phone_clean = '+228' + phone_clean
                elif not phone_clean.startswith('+') and len(phone_clean) == 12 and phone_clean.startswith('228'):
                    phone_clean = '+' + phone_clean
                
                if User.objects.filter(phone_number=phone_clean).exists():
                    messages.error(request, "Un utilisateur existe déjà avec ce numéro de téléphone.")
                else:
                    new_agent = User.objects.create_user(
                        phone_number=phone_clean,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        email=email if email else None,
                        role='AGENT',
                        parent_agency=agency,
                        is_saas_active=True
                    )
                    messages.success(request, f"Collaborateur {new_agent.get_full_name()} créé avec succès !")
                    return redirect('agency_sub_agents')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création : {e}")
        else:
            messages.error(request, "Veuillez renseigner tous les champs obligatoires.")
            
    # Enrich staff with today's attendance, schedules, and BI stats
    import datetime
    today = timezone.now().date()
    thirty_days_ago = today - datetime.timedelta(days=30)
    
    for member in staff:
        member.today_attendance = EmployeeAttendance.objects.filter(employee=member, date=today).first()
        member.schedules_list = EmployeeSchedule.objects.filter(employee=member).order_by('day_of_week')
        # Format weekly planning display
        sched_map = {s.day_of_week: s for s in member.schedules_list}
        member.weekly_planning = []
        for d in range(1, 8):
            if d in sched_map:
                member.weekly_planning.append({
                    'day': d,
                    'active': True,
                    'start': sched_map[d].start_time.strftime("%H:%M"),
                    'end': sched_map[d].end_time.strftime("%H:%M")
                })
            else:
                member.weekly_planning.append({
                    'day': d,
                    'active': False
                })
                
        # --- BI Statistics for the last 30 days ---
        # 1. Total scheduled days in the last 30 days
        scheduled_days_of_week = list(member.schedules_list.values_list('day_of_week', flat=True))
        total_scheduled = 0
        total_scheduled_hours = 0.0
        if scheduled_days_of_week:
            curr = thirty_days_ago
            while curr <= today:
                if curr.isoweekday() in scheduled_days_of_week:
                    total_scheduled += 1
                    s = sched_map.get(curr.isoweekday())
                    if s:
                        start_dt = datetime.datetime.combine(today, s.start_time)
                        end_dt = datetime.datetime.combine(today, s.end_time)
                        if end_dt < start_dt:
                            end_dt += datetime.timedelta(days=1)
                        total_scheduled_hours += (end_dt - start_dt).total_seconds() / 3600.0
                curr += datetime.timedelta(days=1)
        
        # 2. Actual present and late days clocked in
        attendances_30 = EmployeeAttendance.objects.filter(
            employee=member,
            date__range=(thirty_days_ago, today)
        )
        present_days = attendances_30.exclude(status='ABSENT').exclude(clock_in__isnull=True).count()
        late_days = attendances_30.filter(is_late=True).count()
        late_minutes = attendances_30.aggregate(total=Sum('late_minutes'))['total'] or 0
        total_worked_hours = sum([att.total_work_hours for att in attendances_30])
        member.total_worked_hours_30d = round(total_worked_hours, 1)
        member.total_scheduled_hours_30d = round(total_scheduled_hours, 1)
        
        # Calculate Rates
        if total_scheduled > 0:
            member.presence_rate = min(100, round((present_days / total_scheduled) * 100))
            member.absence_days = max(0, total_scheduled - present_days)
            member.absence_rate = max(0, 100 - member.presence_rate)
        else:
            member.presence_rate = 100 if present_days > 0 else 0
            member.absence_days = 0
            member.absence_rate = max(0, 100 - member.presence_rate)
            
        if total_scheduled_hours > 0:
            member.productivity_rate = min(100, round((total_worked_hours / total_scheduled_hours) * 100))
        else:
            member.productivity_rate = 100 if total_worked_hours > 0 else 0
            
        member.present_days = present_days
        member.total_scheduled_days = total_scheduled
        member.late_days = late_days
        member.late_minutes_total = late_minutes
        
        # Lateness rate
        if present_days > 0:
            member.lateness_rate = round((late_days / present_days) * 100)
        else:
            member.lateness_rate = 0
            
        # 3. Productivity (Tasks completion rate)
        tasks_30 = EmployeeTask.objects.filter(
            employee=member,
            created_at__date__range=(thirty_days_ago, today)
        )
        total_tasks = tasks_30.count()
        completed_tasks = tasks_30.filter(status='COMPLETED').count()
        
        member.total_tasks_count = total_tasks
        member.completed_tasks_count = completed_tasks
        if total_tasks > 0:
            member.productivity_rate = round((completed_tasks / total_tasks) * 100)
        else:
            member.productivity_rate = 100  # Default to 100% if no tasks assigned
            
    # All tasks list (generic Foreign Key to User in 'hotel' holds agency)
    tasks = EmployeeTask.objects.filter(hotel=agency).order_by('due_date', '-created_at')
    
    # Attendances list for history
    attendance_history = EmployeeAttendance.objects.filter(hotel=agency).order_by('-date', '-clock_in')[:100]
    
    # Today presence summary
    today_attendances = EmployeeAttendance.objects.filter(hotel=agency, date=today)
    present_count = today_attendances.filter(status__in=['PRESENT', 'LATE', 'ON_BREAK']).count()
    late_count = today_attendances.filter(status='LATE').count()
            
    context = {
        'staff': staff,
        'staff_count': staff_count,
        'tasks': tasks,
        'attendance_history': attendance_history,
        'present_count': present_count,
        'late_count': late_count,
    }
    return render(request, 'agency/agency_sub_agents.html', context)


@login_required
@agency_saas_required
def agency_sub_agent_delete(request, agent_id):
    if hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les administrateurs de l'agence peuvent gérer les collaborateurs.")
        return redirect('agency_dashboard')
        
    agency = request.user
    agent = get_object_or_404(User, id=agent_id, parent_agency=agency, role='AGENT')
    agent.delete()
    messages.success(request, f"Collaborateur supprimé avec succès.")
    return redirect('agency_sub_agents')


@login_required
@agency_saas_required
def agency_clock_action(request):
    """
    Pointage d'arrivée, de départ ou de pause pour le collaborateur de gérance connecté.
    """
    if not hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les collaborateurs peuvent utiliser le pointage.")
        return redirect('agency_dashboard')
        
    employee = request.actual_user
    agency = request.user
    today = timezone.now().date()
    now_dt = timezone.now()
    
    attendance, created = EmployeeAttendance.objects.get_or_create(
        employee=employee,
        hotel=agency, # using the AUTH_USER_MODEL generic ForeignKey
        date=today
    )
    
    action = request.POST.get('action')
    lat_val = request.POST.get('latitude')
    lng_val = request.POST.get('longitude')
    lat = None
    lng = None
    if lat_val and lng_val:
        try:
            from decimal import Decimal
            lat = Decimal(lat_val)
            lng = Decimal(lng_val)
        except Exception:
            pass
            
    if action == 'in':
        if attendance.clock_in:
            messages.warning(request, "Vous avez déjà pointé votre arrivée aujourd'hui.")
        else:
            attendance.clock_in = now_dt
            attendance.status = 'PRESENT'
            if lat and lng:
                attendance.latitude_in = lat
                attendance.longitude_in = lng
            
            # Calcul du retard éventuel par rapport au planning
            day_of_week = today.isoweekday()
            schedule = EmployeeSchedule.objects.filter(employee=employee, day_of_week=day_of_week).first()
            if schedule:
                import datetime
                sched_start = timezone.make_aware(datetime.datetime.combine(today, schedule.start_time))
                if now_dt > sched_start:
                    diff = now_dt - sched_start
                    late_mins = int(diff.total_seconds() // 60)
                    if late_mins > 5:
                        attendance.is_late = True
                        attendance.late_minutes = late_mins
                        attendance.status = 'LATE'
                        messages.warning(request, f"Pointage d'arrivée enregistré avec {late_mins} minutes de retard.")
                        # Notification email au gérant de l'agence
                        try:
                            from logertogo.emails import send_employee_late_notification
                            send_employee_late_notification(agency, employee, late_mins, lat, lng)
                        except Exception as email_err:
                            import logging
                            logging.getLogger('django').error(f"❌ [EMAIL ERROR] Erreur envoi retard agence : {email_err}")
                    else:
                        messages.success(request, "Pointage d'arrivée enregistré à l'heure.")
                else:
                    messages.success(request, "Pointage d'arrivée enregistré à l'heure.")
            else:
                messages.success(request, "Pointage d'arrivée enregistré (aucun planning défini).")
            attendance.save()
            log_employee_action(request, 'CLOCK_IN', f"Pointage d'arrivée enregistré à {now_dt.strftime('%H:%M:%S')} (GPS: {lat or 'N/D'}, {lng or 'N/D'} | Retard: {attendance.late_minutes} min)")
            
    elif action == 'break_start':
        if not attendance.clock_in:
            messages.error(request, "Vous devez d'abord pointer votre arrivée.")
        elif attendance.clock_out:
            messages.error(request, "Votre service est déjà terminé.")
        elif attendance.break_start:
            messages.warning(request, "Vous êtes déjà en pause.")
        else:
            attendance.break_start = now_dt
            attendance.status = 'ON_BREAK'
            attendance.save()
            messages.info(request, "Début de pause enregistré.")
            log_employee_action(request, 'BREAK_START', f"Début de pause enregistré à {now_dt.strftime('%H:%M:%S')}")
            
    elif action == 'break_end':
        if not attendance.break_start:
            messages.error(request, "Vous n'êtes pas en pause.")
        elif attendance.break_end:
            messages.warning(request, "Vous avez déjà repris votre service.")
        else:
            attendance.break_end = now_dt
            attendance.status = 'LATE' if attendance.is_late else 'PRESENT'
            attendance.save()
            messages.success(request, "Reprise de service enregistrée.")
            log_employee_action(request, 'BREAK_END', f"Reprise de service enregistrée à {now_dt.strftime('%H:%M:%S')}")
            
    elif action == 'out':
        if not attendance.clock_in:
            messages.error(request, "Vous devez d'abord pointer votre arrivée.")
        elif attendance.clock_out:
            messages.warning(request, "Vous avez déjà pointé votre départ aujourd'hui.")
        else:
            if attendance.break_start and not attendance.break_end:
                attendance.break_end = now_dt
                
            attendance.clock_out = now_dt
            attendance.status = 'CLOCK_OUT'
            if lat and lng:
                attendance.latitude_out = lat
                attendance.longitude_out = lng
            attendance.save()
            messages.success(request, f"Service terminé. Durée travaillée : {attendance.total_work_hours} heures.")
            log_employee_action(request, 'CLOCK_OUT', f"Pointage de départ enregistré à {now_dt.strftime('%H:%M:%S')} (GPS: {lat or 'N/D'}, {lng or 'N/D'} | Durée : {attendance.total_work_hours} heures)")
            
    return redirect('agency_dashboard')


@login_required
@agency_saas_required
def agency_schedule_save(request):
    """
    Enregistre ou met à jour le planning hebdomadaire d'un collaborateur d'agence.
    """
    if hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les administrateurs de l'agence peuvent modifier le planning.")
        return redirect('agency_dashboard')
        
    agency = request.user
    
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        agent = get_object_or_404(User, id=agent_id, parent_agency=agency, role='AGENT')
        
        EmployeeSchedule.objects.filter(employee=agent).delete()
        
        days_added = 0
        for day_val in range(1, 8):
            enabled = request.POST.get(f'day_{day_val}_enable')
            if enabled:
                start_str = request.POST.get(f'day_{day_val}_start')
                end_str = request.POST.get(f'day_{day_val}_end')
                
                if start_str and end_str:
                    try:
                        import datetime
                        start_time = datetime.datetime.strptime(start_str, "%H:%M").time()
                        end_time = datetime.datetime.strptime(end_str, "%H:%M").time()
                        
                        EmployeeSchedule.objects.create(
                            hotel=agency, # AUTH_USER_MODEL ForeignKey
                            employee=agent,
                            day_of_week=day_val,
                            start_time=start_time,
                            end_time=end_time
                        )
                        days_added += 1
                    except Exception as e:
                        pass
        
        messages.success(request, f"Planning mis à jour avec succès ({days_added} jours configurés).")
        
    return redirect('agency_sub_agents')


@login_required
@agency_saas_required
def agency_task_assign(request):
    """
    Assigne une consigne exceptionnelle à un agent d'agence.
    """
    if hasattr(request, 'actual_user'):
        messages.error(request, "Accès interdit : seuls les gérants de l'agence peuvent assigner des tâches.")
        return redirect('agency_dashboard')
        
    agency = request.user
    
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        due_date_str = request.POST.get('due_date')
        
        agent = get_object_or_404(User, id=agent_id, parent_agency=agency, role='AGENT')
        
        if title and due_date_str:
            try:
                import datetime
                due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
                EmployeeTask.objects.create(
                    hotel=agency, # AUTH_USER_MODEL generic ForeignKey holds agency
                    employee=agent,
                    title=title,
                    description=description or '',
                    due_date=due_date
                )
                messages.success(request, f"Tâche exceptionnelle assignée avec succès à {agent.get_full_name()} !")
            except Exception as e:
                messages.error(request, f"Erreur lors de l'enregistrement de la tâche : {e}")
        else:
            messages.error(request, "Veuillez renseigner un titre et une date d'échéance.")
            
    return redirect('agency_sub_agents')


@login_required
@agency_saas_required
def agency_task_complete(request, task_id):
    """
    Valide l'achèvement d'une tâche exceptionnelle d'agence.
    """
    agency = request.user
    
    if hasattr(request, 'actual_user'):
        task = get_object_or_404(EmployeeTask, id=task_id, hotel=agency, employee=request.actual_user)
    else:
        task = get_object_or_404(EmployeeTask, id=task_id, hotel=agency)
        
    task.status = 'COMPLETED'
    task.completed_at = timezone.now()
    task.save()
    
    # Notification email au gérant de l'agence
    try:
        from logertogo.emails import send_employee_task_completed_notification
        send_employee_task_completed_notification(task.hotel, task.employee, task)
    except Exception as email_err:
        import logging
        logging.getLogger('django').error(f"❌ [EMAIL ERROR] Erreur envoi completion tâche agence : {email_err}")
        
    log_employee_action(request, 'TASK_COMPLETE', f"Consigne d'agence validée : '{task.title}'")
    messages.success(request, f"Tâche '{task.title}' validée et marquée comme terminée !")
    return redirect('agency_dashboard')


@agency_saas_required
def agency_applications(request):
    """
    Vue listant les candidatures, demandes de visite, et réservations provenant du site public.
    """
    agency = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action')
        item_id = request.POST.get('item_id')
        item_type = request.POST.get('item_type') # 'application', 'visit', 'reservation'
        status = request.POST.get('status')
        
        if item_type == 'application':
            obj = get_object_or_404(PropertyApplication, id=item_id, property__owner=agency)
            obj.status = status
            obj.save()
            messages.success(request, f"Statut de la candidature mis à jour: {obj.get_status_display()}")
        elif item_type == 'visit':
            obj = get_object_or_404(VisitRequest, id=item_id, property__owner=agency)
            obj.status = status
            obj.save()
            messages.success(request, f"Statut de la visite mis à jour: {obj.get_status_display()}")
        elif item_type == 'reservation':
            obj = get_object_or_404(Reservation, id=item_id, property__owner=agency)
            obj.status = status
            obj.save()
            messages.success(request, f"Statut de la réservation mis à jour: {obj.get_status_display()}")
            
        return redirect('agency_applications')
    
    applications = PropertyApplication.objects.filter(property__owner=agency).select_related('property', 'tenant').order_by('-created_at')
    visits = VisitRequest.objects.filter(property__owner=agency).select_related('property', 'user').order_by('-created_at')
    reservations = Reservation.objects.filter(property__owner=agency).select_related('property', 'user').order_by('-created_at')
    
    context = {
        'applications': applications,
        'visits': visits,
        'reservations': reservations,
        'app_statuses': PropertyApplication.StatusEnum.choices,
        'res_statuses': Reservation.StatusEnum.choices,
    }
    return render(request, 'agency/agency_applications.html', context)
