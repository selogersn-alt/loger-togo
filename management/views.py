from django.utils.translation import gettext as _
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Lease, RentPayment, MaintenanceRequest
from logersn.models import Property
from users.models import User
from django.utils import timezone
import datetime

@login_required
def landlord_dashboard_view(request):
    """
    Tableau de bord Premium pour les propriétaires/bailleurs et agences.
    """
    if request.user.role == 'TENANT':
        return redirect('management:tenant_dashboard')
    
    section = request.GET.get('section', 'home')
    my_leases = Lease.objects.filter(landlord=request.user).select_related('property', 'tenant')
    my_properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    
    # Statistiques spécifiques aux annonces
    active_ads_count = my_properties.filter(is_published=True).count()
    pending_ads_count = my_properties.filter(is_published=False).count()
    
    # Statistiques de gestion
    active_leases_count = my_leases.filter(status='ACTIVE').count()
    unpaid_rents = RentPayment.objects.filter(lease__landlord=request.user, status='UNPAID').count()
    open_incidents = MaintenanceRequest.objects.filter(lease__landlord=request.user, status='OPEN').count()
    
    # Candidatures
    from logersn.models import PropertyApplication
    my_applications = PropertyApplication.objects.filter(property__owner=request.user).order_by('-created_at')
    
    # Messagerie
    from chat.models import Conversation
    my_conversations = request.user.conversations.all().prefetch_related('participants', 'messages')
    
    # Données pour le graphique (6 derniers mois)
    from django.db.models.functions import TruncMonth
    from django.db.models import Sum
    
    six_months_ago = timezone.now().date() - datetime.timedelta(days=180)
    revenue_data = RentPayment.objects.filter(
        lease__landlord=request.user, 
        status='PAID',
        date_paid__gte=six_months_ago
    ).annotate(month=TruncMonth('date_paid')).values('month').annotate(total=Sum('amount_paid')).order_by('month')
    
    chart_labels = [d['month'].strftime('%b %Y') for d in revenue_data]
    chart_totals = [float(d['total']) for d in revenue_data]
    
    context = {
        'section': section,
        'leases': my_leases,
        'properties': my_properties,
        'applications': my_applications,
        'conversations': my_conversations,
        'stats': {
            'active_leases': active_leases_count,
            'unpaid_rents': unpaid_rents,
            'open_incidents': open_incidents,
            'active_ads': active_ads_count,
            'pending_ads': pending_ads_count,
            'total_ads': my_properties.count(),
        },
        'chart_labels': chart_labels,
        'chart_totals': chart_totals,
    }
    return render(request, 'management/landlord_dashboard.html', context)

@login_required
def tenant_dashboard_view(request):
    """
    Tableau de bord Premium pour les locataires.
    """
    section = request.GET.get('section', 'home')
    my_leases = Lease.objects.filter(tenant=request.user, status='ACTIVE').select_related('property', 'landlord')
    my_payments = RentPayment.objects.filter(lease__tenant=request.user).order_by('-period_start')
    my_incidents = MaintenanceRequest.objects.filter(lease__tenant=request.user).order_by('-created_at')
    
    # Candidatures envoyées
    from logersn.models import PropertyApplication
    my_applications = PropertyApplication.objects.filter(tenant=request.user).order_by('-created_at')
    
    # Messagerie
    my_conversations = request.user.conversations.all().prefetch_related('participants', 'messages')
    
    context = {
        'section': section,
        'leases': my_leases,
        'payments': my_payments,
        'incidents': my_incidents,
        'applications': my_applications,
        'conversations': my_conversations,
        'stats': {
            'active_leases': my_leases.count(),
            'total_applications': my_applications.count(),
            'unread_messages': 0, # TODO: implémenter compteur
        }
    }
    return render(request, 'management/tenant_dashboard.html', context)

@login_required
def create_lease_view(request, property_id=None):
    """
    Créer un nouveau bail pour une propriété.
    """
    if request.user.role == 'TENANT':
        messages.error(request, _("Seuls les bailleurs peuvent créer des baux."))
        return redirect('dashboard')
        
    if request.method == 'POST':
        property_obj = get_object_or_404(Property, id=request.POST.get('property_id'), owner=request.user)
        tenant_phone = request.POST.get('tenant_phone')
        tenant = User.objects.filter(phone_number=tenant_phone, role='TENANT').first()
        
        if not tenant:
            messages.error(request, _("Locataire introuvable avec ce numéro de téléphone."))
            return render(request, 'management/create_lease.html', {'properties': Property.objects.filter(owner=request.user)})

        lease = Lease.objects.create(
            property=property_obj,
            tenant=tenant,
            landlord=request.user,
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date') or None,
            rent_amount=request.POST.get('rent_amount') or property_obj.price,
            deposit_amount=request.POST.get('deposit_amount', 0),
            custom_contract_terms=request.POST.get('custom_contract_terms'),
            custom_header_text=request.POST.get('custom_header_text'),
            status='ACTIVE'
        )
        
        messages.success(request, _("Bail créé avec succès pour %(name)s !") % {'name': tenant.get_full_name()})
        return redirect('landlord_dashboard')
        
    properties = Property.objects.filter(owner=request.user)
    return render(request, 'management/create_lease.html', {'properties': properties, 'selected_property_id': property_id})

from .utils import render_to_pdf

@login_required
def download_lease_pdf_view(request, lease_id):
    """
    Génère et télécharge le contrat de bail au format PDF.
    """
    lease = get_object_or_404(Lease, id=lease_id)
    # Sécurité : Seul le bailleur ou le locataire peut voir le PDF
    if request.user != lease.landlord and request.user != lease.tenant:
        messages.error(request, _("Accès refusé."))
        return redirect('dashboard')
    
    context = {
        'lease': lease,
        'today': timezone.now().date(),
        'company_name': "Loger Togo (DigitalH Group)",
    }
    pdf = render_to_pdf('management/pdf/lease_contract.html', context)
    if pdf:
        response = HttpResponse(pdf.content, content_type='application/pdf')
        filename = f"Contrat_Bail_{lease.property.neighborhood}_{lease.tenant.last_name}.pdf"
        content = f"inline; filename={filename}"
        response['Content-Disposition'] = content
        return response
    return HttpResponse(_("Erreur lors de la génération du PDF"), status=400)

@login_required
def download_receipt_pdf_view(request, payment_id):
    """
    Génère et télécharge la quittance de loyer au format PDF.
    """
    payment = get_object_or_404(RentPayment, id=payment_id)
    # Sécurité
    if request.user != payment.lease.landlord and request.user != payment.lease.tenant:
        messages.error(request, _("Accès refusé."))
        return redirect('dashboard')
    
    context = {
        'payment': payment,
        'lease': payment.lease,
        'today': timezone.now().date(),
    }
    pdf = render_to_pdf('management/pdf/rent_receipt.html', context)
    if pdf:
        response = HttpResponse(pdf.content, content_type='application/pdf')
        filename = f"Quittance_{payment.period_start.strftime('%m_%Y')}_{payment.lease.tenant.last_name}.pdf"
        content = f"inline; filename={filename}"
        response['Content-Disposition'] = content
        return response
    return HttpResponse(_("Erreur lors de la génération du PDF"), status=400)

from logertogo.emails import (
    send_rent_paid_email, send_incident_reported_email, 
    send_incident_status_update_email
)

@login_required
def report_incident_view(request, lease_id):
    """
    Permet au locataire de signaler un incident (panne, fuite, etc.).
    """
    lease = get_object_or_404(Lease, id=lease_id, tenant=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 'MEDIUM')
        
        incident = MaintenanceRequest.objects.create(
            lease=lease,
            title=title,
            description=description,
            priority=priority,
            status='OPEN'
        )
        # Notification Email au bailleur
        send_incident_reported_email(incident)
        
        messages.success(request, _("Incident signalé avec succès au bailleur."))
        return redirect('tenant_dashboard')
        
    return render(request, 'management/report_incident.html', {'lease': lease})

@login_required
def update_incident_status_view(request, incident_id):
    """
    Permet au bailleur de mettre à jour le statut d'un incident.
    """
    incident = get_object_or_404(MaintenanceRequest, id=incident_id, lease__landlord=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        incident.status = new_status
        incident.save()
        
        # Notification Email au locataire
        send_incident_status_update_email(incident)
        
        messages.success(request, _("Statut de l'incident mis à jour : %(status)s") % {'status': incident.get_status_display()})
        return redirect('landlord_dashboard')
        
@login_required
def mediation_room_view(request, incident_id):
    from chat.models import Conversation, Message
    incident = get_object_or_404(MaintenanceRequest, id=incident_id)
    
    # Vérification des permissions
    lease = incident.lease
    if request.user != lease.landlord and request.user != lease.tenant:
        messages.error(request, _("Accès refusé."))
        return redirect('dashboard')
        
    # Trouver ou créer la conversation
    conversation = Conversation.objects.filter(
        topic=Conversation.TopicEnum.INCIDENT_CLAIM,
        participants=lease.landlord
    ).filter(participants=lease.tenant).first()
    
    if not conversation:
        conversation = Conversation.objects.create(
            topic=Conversation.TopicEnum.INCIDENT_CLAIM
        )
        conversation.participants.add(lease.landlord, lease.tenant)
        
    if request.method == 'POST' and not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            conversation.save()
            return redirect('management:mediation_room', incident_id=incident_id)

    messages_qs = conversation.messages.all().order_by('created_at')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/chat_messages.html', {
            'messages': messages_qs,
            'conversation': conversation
        })
        
    return render(request, 'mediation_room.html', {
        'incident': incident,
        'conversation': conversation,
        'messages': messages_qs,
        'lease': lease
    })
    return redirect('landlord_dashboard')

from .models import TenantDocument

@login_required
def tenant_dossier_view(request):
    """
    Gestion du dossier numérique du locataire.
    """
    if request.method == 'POST' and request.FILES.get('file'):
        doc_type = request.POST.get('document_type')
        file = request.FILES.get('file')
        
        TenantDocument.objects.create(
            user=request.user,
            document_type=doc_type,
            file=file
        )
        messages.success(request, _("Document ajouté à votre dossier avec succès."))
        return redirect('management:tenant_dossier')

    documents = TenantDocument.objects.filter(user=request.user)
    return render(request, 'management/tenant_dossier.html', {'documents': documents})

@login_required
def tenant_dossier_view_for_landlord(request, tenant_id):
    """
    Permet au bailleur de voir le dossier d'un de ses locataires.
    """
    # Sécurité : vérifier que le demandeur est bien le bailleur de ce locataire
    has_lease = Lease.objects.filter(landlord=request.user, tenant_id=tenant_id).exists()
    if not has_lease:
        messages.error(request, _("Accès refusé. Ce locataire n'est pas lié à vos baux."))
        return redirect('landlord_dashboard')
    
    tenant = get_object_or_404(User, id=tenant_id)
    documents = TenantDocument.objects.filter(user=tenant)
    return render(request, 'management/landlord_view_dossier.html', {
        'tenant': tenant,
        'documents': documents
    })

@login_required
def send_payment_reminders_view(request):
    """
    Déclenche l'envoi de rappels pour tous les loyers impayés du bailleur.
    """
    unpaid_payments = RentPayment.objects.filter(
        lease__landlord=request.user, 
        status='UNPAID'
    ).select_related('lease__tenant')
    
    count = 0
    from logertogo.emails import send_payment_reminder_email
    
    for payment in unpaid_payments:
        # Envoyer email (logic à définir dans emails.py)
        send_payment_reminder_email(payment)
        count += 1
        
    messages.success(request, _("%(count)s rappel(s) envoyé(s) avec succès aux locataires.") % {'count': count})
    return redirect('landlord_dashboard')

import csv
from django.http import HttpResponse

@login_required
def export_accounting_csv_view(request):
    """
    Exporte l'historique financier du bailleur au format CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="comptabilite_{request.user.last_name}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date Paiement', 'Bien', 'Locataire', 'Période', 'Montant Dû', 'Montant Payé', 'Statut'])
    
    payments = RentPayment.objects.filter(lease__landlord=request.user).order_by('-period_start')
    
    for p in payments:
        writer.writerow([
            p.date_paid or 'Non payé',
            p.lease.property.title,
            p.lease.tenant.get_full_name(),
            f"{p.period_start} au {p.period_end}",
            p.amount_due,
            p.amount_paid,
            p.get_status_display()
        ])
        
    return response

@login_required
def record_payment_view(request, lease_id):
    """
    Enregistrer un paiement de loyer.
    """
    lease = get_object_or_404(Lease, id=lease_id, landlord=request.user)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        period_start = request.POST.get('period_start')
        # Calcul auto de la fin du mois
        start_dt = datetime.datetime.strptime(period_start, '%Y-%m-%d')
        period_end = (start_dt + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
        
        payment = RentPayment.objects.create(
            lease=lease,
            period_start=period_start,
            period_end=period_end,
            amount_due=lease.rent_amount,
            amount_paid=amount,
            status='PAID' if float(amount) >= float(lease.rent_amount) else 'PARTIAL',
            date_paid=timezone.now().date()
        )
        # Notification Email (Locataire + Bailleur)
        send_rent_paid_email(payment)
        
        messages.success(request, _("Paiement enregistré !"))
        return redirect('landlord_dashboard')
        
    return render(request, 'management/record_payment.html', {'lease': lease})

@login_required
def update_application_status(request, app_id):
    """
    Permet au bailleur de changer le statut d'une candidature.
    """
    from logersn.models import PropertyApplication
    application = get_object_or_404(PropertyApplication, id=app_id)
    
    # Sécurité : seul le proprio du bien peut changer le statut
    if application.property.owner != request.user:
        messages.error(request, _("Action non autorisée."))
        return redirect('dashboard')
        
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['ACCEPTED', 'REFUSED']:
            application.status = new_status
            application.save()
            messages.success(request, _("Candidature mise à jour : %(status)s") % {'status': application.get_status_display()})
            
    return redirect(f"{reverse('management:landlord_dashboard')}?section=applications")
