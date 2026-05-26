from django.utils.translation import gettext as _
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Lease, RentPayment, MaintenanceRequest, PropertyInventory
from logersn.models import Property
from users.models import User
from django.utils import timezone
import datetime

@login_required
def landlord_dashboard_view(request):
    """
    Tableau de bord Premium pour les propriétaires/bailleurs et agences.
    Redirigé vers le sous-domaine agence.
    """
    return redirect('http://agence.logertogo.com/')

@login_required
def tenant_dashboard_view(request):
    """
    Tableau de bord Premium pour les locataires.
    """
    section = request.GET.get('section', 'home')
    my_leases = Lease.objects.filter(tenant=request.user, status='ACTIVE').select_related('property', 'landlord')
    my_payments = RentPayment.objects.filter(lease__tenant=request.user).order_by('-period_start')
    my_incidents = MaintenanceRequest.objects.filter(lease__tenant=request.user).order_by('-created_at')
    my_inventories = PropertyInventory.objects.filter(lease__tenant=request.user).order_by('-inventory_date')
    
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
        'inventories': my_inventories,
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
    Redirigé vers le sous-domaine agence.
    """
    return redirect('http://agence.logertogo.com/')

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
    Redirigé vers le sous-domaine agence.
    """
    return redirect('http://agence.logertogo.com/')

@login_required
def send_payment_reminders_view(request):
    """
    Déclenche l'envoi de rappels pour tous les loyers impayés du bailleur.
    Redirigé vers le sous-domaine agence.
    """
    return redirect('http://agence.logertogo.com/')

import csv
from django.http import HttpResponse

@login_required
def export_accounting_csv_view(request):
    """
    Exporte l'historique financier du bailleur au format CSV.
    Redirigé vers le sous-domaine agence.
    """
    return redirect('http://agence.logertogo.com/')

@login_required
def record_payment_view(request, lease_id):
    """
    Enregistrer un paiement de loyer.
    Redirigé vers le sous-domaine agence.
    """
    return redirect('http://agence.logertogo.com/')

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
