from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from logersn.models import Property
from solvable.models import PropertyApplication

from rest_framework import viewsets
from .models import RentalFiliation, IncidentReport, PaymentHistory
from .serializers import RentalFiliationSerializer, IncidentReportSerializer, PaymentHistorySerializer

class RentalFiliationViewSet(viewsets.ModelViewSet):
    queryset = RentalFiliation.objects.all()
    serializer_class = RentalFiliationSerializer

class IncidentReportViewSet(viewsets.ModelViewSet):
    queryset = IncidentReport.objects.all()
    serializer_class = IncidentReportSerializer

class PaymentHistoryViewSet(viewsets.ModelViewSet):
    queryset = PaymentHistory.objects.all()
    serializer_class = PaymentHistorySerializer


@login_required
def report_incident_view(request):
    from solvable.forms import IncidentReportForm
    from solvable.models import RentalFiliation
    from users.models import NILS_Profile, User
    
    filiation_id = request.GET.get('filiation', None)
    
    if request.method == 'POST':
        form = IncidentReportForm(request.POST, request.FILES, landlord=request.user)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reporter = request.user
            
            # Si une filiation est fournie
            if incident.rental_filiation:
                incident.reported_tenant = incident.rental_filiation.tenant
                # Vérifier si c'est de la vente (interdit de signaler)
                if incident.rental_filiation.property and incident.rental_filiation.property.listing_category == 'SALE':
                    messages.error(request, "Impossible de signaler un incident sur un bien en vente.")
                    return redirect('dashboard')
            else:
                # Signalement direct sans contrat app
                reported_phone = request.POST.get('reported_phone')
                if reported_phone:
                    # Chercher si le locataire existe
                    tenant = User.objects.filter(phone_number__icontains=reported_phone).first()
                    if tenant:
                        incident.reported_tenant = tenant
                incident.reported_phone = reported_phone
                incident.reported_name = request.POST.get('reported_name')
                incident.property_address = request.POST.get('property_address')

            # Logique de bénéficiaire
            beneficiary_nils = form.cleaned_data.get('landlord_nils_beneficiary')
            if beneficiary_nils:
                try:
                    prof = NILS_Profile.objects.get(nils_number__iexact=beneficiary_nils)
                    incident.beneficiary = prof.user
                except NILS_Profile.DoesNotExist:
                    incident.beneficiary = request.user
            else:
                incident.beneficiary = incident.rental_filiation.landlord if incident.rental_filiation else request.user
                
            incident.is_validated = False
            incident.save()
            
            messages.success(request, "Signalement enregistré et soumis à validation.")
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
            if request.user.nils_profile:
                request.user.nils_profile.update_score()
                
            messages.success(request, "Message envoyé.")
            return redirect('mediation_room', item_type=item_type, item_id=item_id)
            
    messages_list = item.mediation_messages.all().order_by('created_at') if hasattr(item, 'mediation_messages') else []
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/mediation_messages.html', {'mediation_messages': messages_list, 'request': request})
    
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
                monthly_rent=application.property.price,
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

