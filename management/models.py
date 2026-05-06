import uuid
from django.db import models
from django.conf import settings
from logersn.models import Property

User = settings.AUTH_USER_MODEL

class Lease(models.Model):
    """
    Contrat de bail entre un bailleur et un locataire pour un bien donné.
    """
    class StatusEnum(models.TextChoices):
        PENDING = 'PENDING', 'En attente de signature'
        ACTIVE = 'ACTIVE', 'Actif'
        TERMINATED = 'TERMINATED', 'Terminé'
        CANCELLED = 'CANCELLED', 'Annulé'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='leases')
    tenant = models.ForeignKey(User, on_delete=models.PROTECT, related_name='tenant_leases')
    landlord = models.ForeignKey(User, on_delete=models.PROTECT, related_name='landlord_leases')
    
    start_date = models.DateField(verbose_name="Date de début")
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin (Optionnelle)")
    
    rent_amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Loyer mensuel (FCFA)")
    deposit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Dépôt de garantie (Caution)")
    
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.PENDING)
    contract_pdf = models.FileField(upload_to='contracts/', null=True, blank=True, verbose_name="Contrat signé (PDF)")
    
    custom_contract_terms = models.TextField(null=True, blank=True, verbose_name="Clauses particulières (Personnalisation)")
    custom_header_text = models.CharField(max_length=255, null=True, blank=True, verbose_name="En-tête personnalisé (ex: Agence Digitale)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bail"
        verbose_name_plural = "Baux"
        ordering = ['-created_at']

    def __str__(self):
        return f"Bail: {self.property.title} - {self.tenant.get_full_name()}"

class RentPayment(models.Model):
    """
    Suivi des paiements de loyer pour un bail.
    """
    class StatusEnum(models.TextChoices):
        UNPAID = 'UNPAID', 'Impayé'
        PARTIAL = 'PARTIAL', 'Partiel'
        PAID = 'PAID', 'Payé'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments')
    
    period_start = models.DateField(verbose_name="Période du")
    period_end = models.DateField(verbose_name="Période au")
    
    amount_due = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Montant dû")
    amount_paid = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Montant payé")
    
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.UNPAID)
    date_paid = models.DateField(null=True, blank=True, verbose_name="Date de paiement")
    
    receipt_pdf = models.FileField(upload_to='receipts/', null=True, blank=True, verbose_name="Quittance de loyer (PDF)")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Paiement de Loyer"
        verbose_name_plural = "Paiements de Loyers"
        ordering = ['-period_start']

    def __str__(self):
        return f"Loyer {self.period_start.strftime('%m/%Y')} - {self.lease.tenant}"

class MaintenanceRequest(models.Model):
    """
    Demandes d'entretien ou incidents signalés par le locataire.
    """
    class PriorityEnum(models.TextChoices):
        LOW = 'LOW', 'Basse'
        MEDIUM = 'MEDIUM', 'Moyenne'
        HIGH = 'HIGH', 'Haute'
        URGENT = 'URGENT', 'Urgent'

    class StatusEnum(models.TextChoices):
        OPEN = 'OPEN', 'Ouvert'
        IN_PROGRESS = 'IN_PROGRESS', 'En cours'
        RESOLVED = 'RESOLVED', 'Résolu'
        CLOSED = 'CLOSED', 'Fermé'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='incidents')
    
    title = models.CharField(max_length=255, verbose_name="Titre de l'incident")
    description = models.TextField(verbose_name="Description détaillée")
    
    priority = models.CharField(max_length=10, choices=PriorityEnum.choices, default=PriorityEnum.MEDIUM)
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.OPEN)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Demande d'entretien"
        verbose_name_plural = "Demandes d'entretien"
        ordering = ['-created_at']

    def __str__(self):
        return f"Incident: {self.title} ({self.get_status_display()})"

class TenantDocument(models.Model):
    """
    Dossier numérique du locataire (CNI, Attestations, Quittances...).
    """
    class DocTypeEnum(models.TextChoices):
        ID_CARD = 'ID_CARD', 'Pièce d\'identité (CNI/Passeport)'
        EMPLOYMENT = 'EMPLOYMENT', 'Attestation d\'emploi'
        PAYSLIP = 'PAYSLIP', 'Fiche de paie'
        OLD_RECEIPT = 'OLD_RECEIPT', 'Ancienne quittance'
        OTHER = 'OTHER', 'Autre document'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_documents')
    
    document_type = models.CharField(max_length=20, choices=DocTypeEnum.choices)
    file = models.FileField(upload_to='tenant_dossiers/%Y/%m/', verbose_name="Fichier")
    
    is_verified = models.BooleanField(default=False, verbose_name="Vérifié par Loger Togo")
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Document Locataire"
        verbose_name_plural = "Documents Locataires"

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.user.get_full_name()}"
