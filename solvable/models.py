import uuid
from django.db import models
from django.conf import settings
from logersn.models import Property 
from django.utils import timezone
import datetime

User = settings.AUTH_USER_MODEL

class RentalFiliation(models.Model):
    class StatusEnum(models.TextChoices):
        PENDING_APPROVAL = 'PENDING_APPROVAL', 'En attente d\'approbation'
        ACTIVE = 'ACTIVE', 'Actif'
        TERMINATION_REQUESTED = 'TERMINATION_REQUESTED', 'Résiliation demandée'
        TERMINATED = 'TERMINATED', 'Terminé'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='filiations')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_filiations')
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='landlord_filiations')
    monthly_rent = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=StatusEnum.choices, default=StatusEnum.PENDING_APPROVAL)
    
    # Notations mutuelles (1 à 10)
    rating_for_landlord = models.IntegerField(null=True, blank=True, verbose_name="Note du locataire pour le bailleur")
    rating_for_tenant = models.IntegerField(null=True, blank=True, verbose_name="Note du bailleur pour le locataire")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Filiation landlord: {self.landlord.phone_number} <-> tenant: {self.tenant.phone_number}"

def default_mediation_end():
    return timezone.now() + datetime.timedelta(days=30)

class IncidentReport(models.Model):
    class StatusEnum(models.TextChoices):
        IN_MEDIATION = 'IN_MEDIATION', 'In Mediation'
        RESOLVED = 'RESOLVED', 'Resolved'
        IMPACTED = 'IMPACTED', 'Impacted on NILS'
        
    class IncidentTypeEnum(models.TextChoices):
        UNPAID_RENT = 'UNPAID_RENT', 'Loyer impayé'
        UNPAID_COMMISSION = 'UNPAID_COMMISSION', 'Commission impayée (Courtage)'
        LATE_PAYMENT = 'LATE_PAYMENT', 'Retard de paiement'
        PROPERTY_DAMAGE = 'PROPERTY_DAMAGE', 'Dégradation du bien'
        BAD_BEHAVIOR = 'BAD_BEHAVIOR', 'Mauvais comportement / Conflit'
        OTHER = 'OTHER', 'Autre'

    class NotifierTypeEnum(models.TextChoices):
        SELF = 'SELF', 'Pour moi-même (Propriétaire / Bailleur)'
        INTERMEDIARY = 'INTERMEDIARY', 'Pour le compte d\'un client tiers (Mandat)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rental_filiation = models.ForeignKey(RentalFiliation, on_delete=models.CASCADE, related_name='incidents', null=True, blank=True, help_text="Optionnel si pas de contrat direct dans l'app")
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_incidents')
    notifier_role = models.CharField(max_length=20, choices=NotifierTypeEnum.choices, default=NotifierTypeEnum.SELF, verbose_name="Rôle du déclarant")
    
    reported_tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidents_against_me', null=True, blank=True)
    reported_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Téléphone de la personne signalée (si pas encore sur l'app)")
    reported_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Nom de la personne signalée")
    
    property_address = models.CharField(max_length=255, null=True, blank=True, verbose_name="Adresse du bien concerné (si pas via contrat app)")
    incident_type = models.CharField(max_length=50, choices=IncidentTypeEnum.choices, default=IncidentTypeEnum.UNPAID_RENT)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Seulement pour les loyers impayés ou dégradations")
    description = models.TextField()
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.IN_MEDIATION)
    
    # Mode Contestation Locataire
    is_contested = models.BooleanField(default=False)
    contestation_reason = models.TextField(null=True, blank=True, verbose_name="Motif de contestation")
    
    # Preuves et Validation Admin
    evidence_file = models.FileField(upload_to='incident_evidence/', null=True, blank=True, verbose_name="Document de preuve (Obligatoire)")
    is_validated = models.BooleanField(default=False, verbose_name="Validé par l'Admin")
    beneficiary = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_incident_claims', verbose_name="Bénéficiaire final de la dette")
    
    created_at = models.DateTimeField(auto_now_add=True)
    mediation_end_date = models.DateTimeField(default=default_mediation_end)

    def __str__(self):
        return f"Incident {self.id} for Filiation {self.rental_filiation.id}"

class PaymentHistory(models.Model):
    class StatusEnum(models.TextChoices):
        PAID = 'PAID', 'Payé à temps'
        LATE = 'LATE', 'Payé en retard'
        UNPAID = 'UNPAID', 'Impayé'
        REPORTED = 'REPORTED', 'Signalé (Litige en cours)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rental_filiation = models.ForeignKey(RentalFiliation, on_delete=models.CASCADE, related_name='payments')
    month_year = models.DateField(verbose_name="Mois et Année du Loyer (1er du mois)")
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.PAID)
    payment_proof = models.FileField(upload_to='payment_proofs/', null=True, blank=True, verbose_name="Preuve de paiement (Optionnel)")
    notes = models.TextField(null=True, blank=True, verbose_name="Commentaire (Optionnel)")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    
    # Mode Contestation Locataire
    is_contested = models.BooleanField(default=False)
    contestation_reason = models.TextField(null=True, blank=True, verbose_name="Motif de contestation")

    def __str__(self):
        return f"Payment {self.month_year} - {self.status}"

class PropertyApplication(models.Model):
    class StatusEnum(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        INTERESTED = 'INTERESTED', 'Intéressé (à visiter)'
        REJECTED = 'REJECTED', 'Refusé'
        ACCEPTED = 'ACCEPTED', 'Accepté pour location'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_applications')
    message = models.TextField(blank=True, null=True, verbose_name="Message au bailleur")
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)


class MediationMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Target can be an IncidentReport or a PaymentHistory
    incident = models.ForeignKey(IncidentReport, on_delete=models.CASCADE, related_name='mediation_messages', null=True, blank=True)
    payment = models.ForeignKey(PaymentHistory, on_delete=models.CASCADE, related_name='mediation_messages', null=True, blank=True)
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mediation_sent_messages')
    content = models.TextField()
    is_from_mediator = models.BooleanField(default=False, verbose_name="Envoyé par le médiateur DigitalH")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mediation message from {self.sender} at {self.created_at}"

class ProfessionalFraudReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pro_reports_made')
    
    # Identification du Pro (inscrit ou non)
    reported_pro_name = models.CharField(max_length=255, verbose_name="Nom du Professionnel / Agence")
    reported_pro_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone (si connu)")
    reported_pro_email = models.CharField(max_length=150, blank=True, null=True, verbose_name="Email (si connu)")
    
    reported_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_against_me_pro', verbose_name="Utilisateur inscrit (si match trouvé)")
    
    fraud_description = models.TextField(verbose_name="Détails de la fraude ou dette")
    proof_file = models.FileField(upload_to='pro_fraud_proofs/', verbose_name="Preuve (Reçu, Photo, Screenshot)")
    
    is_validated = models.BooleanField(default=False, verbose_name="Validé par DigitalH Admin")
    is_critical_alert = models.BooleanField(default=False, verbose_name="Afficher en Alerte Critique (Bande défilante)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fraud Report against {self.reported_pro_name} by {self.reporter}"

    class Meta:
        verbose_name = "Signalement de Fraude Pro"
        verbose_name_plural = "Signalements de Fraude Pro"

class PlatformPricing(models.Model):
    service_name = models.CharField(max_length=100, unique=True, verbose_name="Nom du service")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Prix (FCFA)")
    description = models.TextField(blank=True, verbose_name="Description pour l'utilisateur")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    def __str__(self):
        return f"{self.service_name} - {self.price} FCFA"

    class Meta:
        verbose_name = "Paramétrage Tarif"
        verbose_name_plural = "Paramétrage Tarifs"
