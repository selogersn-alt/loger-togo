import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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
    
    rent_amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Loyer mensuel (FCFA)", validators=[MinValueValidator(0)])
    
    deposit_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Dépôt de garantie (Caution)", validators=[MinValueValidator(0)])
    
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.PENDING)
    contract_pdf = models.FileField(upload_to='contracts/', null=True, blank=True, verbose_name="Contrat signé (PDF)")
    
    custom_contract_terms = models.TextField(null=True, blank=True, verbose_name="Clauses particulières (Personnalisation)")
    custom_header_text = models.CharField(max_length=255, null=True, blank=True, verbose_name="En-tête personnalisé (ex: Agence Digitale)")
    
    payment_due_day = models.IntegerField(
        default=5, 
        verbose_name="Jour d'échéance de paiement", 
        validators=[MinValueValidator(1), MaxValueValidator(28)],
        help_text="Jour limite de paiement dans le mois (ex: 5 pour payer avant le 5 du mois)"
    )
    
    template = models.ForeignKey(
        'ContractTemplate', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='leases', 
        verbose_name="Modèle de contrat"
    )
    
    is_signed_by_tenant = models.BooleanField(default=False, verbose_name="Signé par le locataire")
    is_signed_by_landlord = models.BooleanField(default=False, verbose_name="Signé par le bailleur/agence")
    tenant_otp = models.CharField(max_length=6, blank=True, null=True, verbose_name="Code OTP Locataire")
    landlord_otp = models.CharField(max_length=6, blank=True, null=True, verbose_name="Code OTP Bailleur")
    signed_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de signature finale")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bail"
        verbose_name_plural = "Baux"
        ordering = ['-created_at']

    def __str__(self):
        return f"Bail: {self.property.title} - {self.tenant.get_full_name()}"

    @property
    def unique_ref(self):
        """Référence unique du contrat de bail"""
        return f"CTR-{str(self.id)[:8].upper()}"

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
    
    amount_due = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Montant dû", validators=[MinValueValidator(0)])
    amount_paid = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Montant payé", validators=[MinValueValidator(0)])
    
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.UNPAID)
    date_paid = models.DateField(null=True, blank=True, verbose_name="Date de paiement")
    
    receipt_pdf = models.FileField(upload_to='receipts/', null=True, blank=True, verbose_name="Quittance de loyer (PDF)")
    
    payment_method = models.CharField(max_length=50, null=True, blank=True, verbose_name="Mode de paiement")
    receipt_logo = models.FileField(upload_to='receipt_logos/', null=True, blank=True, verbose_name="Logo de la quittance")
    receipt_header = models.CharField(max_length=255, null=True, blank=True, verbose_name="En-tête personnalisé")
    receipt_footer = models.TextField(null=True, blank=True, verbose_name="Pied de page personnalisé")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Paiement de Loyer"
        verbose_name_plural = "Paiements de Loyers"
        ordering = ['-period_start']

    def __str__(self):
        return f"Loyer {self.period_start.strftime('%m/%Y')} - {self.lease.tenant}"

    @builtins.property
    def unique_ref(self):
        """Référence unique de la quittance de loyer"""
        return f"QTC-{str(self.id)[:8].upper()}"

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

    @builtins.property
    def unique_ref(self):
        """Référence unique du ticket d'incident"""
        return f"TKT-{str(self.id)[:8].upper()}"

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

class AgencyClient(models.Model):
    class ClientStatus(models.TextChoices):
        PROSPECT = 'PROSPECT', 'Prospect'
        ACTIVE = 'ACTIVE', 'Actif'
        INACTIVE = 'INACTIVE', 'Inactif'
    
    class ClientType(models.TextChoices):
        TENANT = 'TENANT', 'Locataire'
        LANDLORD = 'LANDLORD', 'Bailleur'
        PARTNER = 'PARTNER', 'Partenaire'
        OTHER = 'OTHER', 'Autre'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agency_clients')
    full_name = models.CharField(max_length=255, verbose_name="Nom complet")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    client_type = models.CharField(max_length=20, choices=ClientType.choices, default=ClientType.TENANT)
    status = models.CharField(max_length=20, choices=ClientStatus.choices, default=ClientStatus.PROSPECT)
    pipeline_stage = models.IntegerField(default=1, verbose_name="Étape de Pipeline (1-5)", validators=[MinValueValidator(1), MaxValueValidator(5)]) # Kanban stage (e.g. 1: Prospecting, 2: Contacted, 3: Visit, 4: Negotiation, 5: Signed)
    notes = models.TextField(null=True, blank=True, verbose_name="Notes / Détails")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Client d'Agence"
        verbose_name_plural = "Clients d'Agence"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.get_client_type_display()})"


class ContractTemplate(models.Model):
    """
    Modèle de contrat de bail personnalisable par chaque agence.
    Contient le texte type du bail avec des variables de substitution.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contract_templates', null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name="Titre du modèle")
    content = models.TextField(
        verbose_name="Contenu du contrat", 
        help_text="Utilisez les balises de substitution : [LOCATAIRE], [PROPRIETAIRE], [BIEN], [LOYER], [CAUTION], [DATE_DEBUT], [DATE_FIN]"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Modèle de contrat"
        verbose_name_plural = "Modèles de contrats"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.agency.get_full_name()}"


class PropertyInventory(models.Model):
    """
    État des lieux (entrée ou sortie) pour un bail locatif.
    """
    class TypeEnum(models.TextChoices):
        IN = 'IN', 'Entrée'
        OUT = 'OUT', 'Sortie'

    class ConditionEnum(models.TextChoices):
        NEW = 'NEW', 'Neuf'
        GOOD = 'GOOD', 'Bon état'
        FAIR = 'FAIR', 'État d\'usage'
        BAD = 'BAD', 'Mauvais état'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='inventories', verbose_name="Bail")
    inventory_type = models.CharField(max_length=5, choices=TypeEnum.choices, default=TypeEnum.IN, verbose_name="Type d'état des lieux")
    inventory_date = models.DateField(verbose_name="Date de l'état des lieux")
    general_condition = models.CharField(max_length=10, choices=ConditionEnum.choices, default=ConditionEnum.GOOD, verbose_name="État général")
    
    details_json = models.TextField(help_text="Stockage JSON structuré des pièces et composants de l'état des lieux")
    
    signature_tenant = models.TextField(null=True, blank=True, help_text="Signature en Base64 du locataire")
    signature_agent = models.TextField(null=True, blank=True, help_text="Signature en Base64 de l'agent/bailleur")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "État des lieux"
        verbose_name_plural = "États des lieux"
        ordering = ['-inventory_date', '-created_at']

    def __str__(self):
        return f"État des lieux ({self.get_inventory_type_display()}) - {self.lease.property.title}"


class HotelRoom(models.Model):
    class TypeEnum(models.TextChoices):
        SINGLE = 'SINGLE', 'Chambre Simple'
        DOUBLE = 'DOUBLE', 'Chambre Double'
        TWIN = 'TWIN', 'Chambre Twin'
        SUITE = 'SUITE', 'Suite'
        DELUXE = 'DELUXE', 'Suite Deluxe'
        DORMITORY = 'DORMITORY', 'Dortoir'

    class StatusEnum(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Disponible'
        OCCUPIED = 'OCCUPIED', 'Occupée'
        CLEANING = 'CLEANING', 'En cours de ménage'
        MAINTENANCE = 'MAINTENANCE', 'En maintenance'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotel_rooms')
    room_number = models.CharField(max_length=50, verbose_name="Numéro de chambre / Nom")
    room_type = models.CharField(max_length=20, choices=TypeEnum.choices, default=TypeEnum.SINGLE)
    price_per_night = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Prix par nuitée (FCFA)", validators=[MinValueValidator(0)])
    price_per_hour = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Prix par heure (FCFA) - Optionnel", validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.AVAILABLE)
    
    # Équipements
    wifi = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)
    minibar = models.BooleanField(default=False)
    tv = models.BooleanField(default=False)
    safe = models.BooleanField(default=False)
    balcony = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chambre d'Hôtel"
        verbose_name_plural = "Chambres d'Hôtel"
        unique_together = ('hotel', 'room_number')

    def __str__(self):
        return f"{self.room_number} - {self.get_room_type_display()}"


class HotelBooking(models.Model):
    class StatusEnum(models.TextChoices):
        PENDING = 'PENDING', 'Confirmée'
        CHECKED_IN = 'CHECKED_IN', 'Client Arrivé (Check-in)'
        CHECKED_OUT = 'CHECKED_OUT', 'Client Parti (Check-out)'
        CANCELLED = 'CANCELLED', 'Annulée'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(HotelRoom, on_delete=models.CASCADE, related_name='bookings')
    client_name = models.CharField(max_length=255, verbose_name="Nom complet du client")
    client_phone = models.CharField(max_length=50, verbose_name="Téléphone")
    client_email = models.EmailField(blank=True, null=True, verbose_name="Email")
    client_id_card = models.CharField(max_length=100, blank=True, null=True, verbose_name="Pièce d'identité")
    
    check_in = models.DateTimeField(verbose_name="Date/Heure d'arrivée")
    check_out = models.DateTimeField(verbose_name="Date/Heure de départ")
    
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.PENDING)
    
    amount_due = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Montant hébergement", default=0)
    amount_paid = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Montant payé", default=0)
    
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mode de paiement")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes / Demandes spéciales")
    shift = models.ForeignKey('HotelShift', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings', verbose_name="Shift de caisse")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Réservation d'Hôtel"
        verbose_name_plural = "Réservations d'Hôtel"

    def __str__(self):
        return f"Res: {self.client_name} - Chambre {self.room.room_number}"

    @property
    def extra_charges(self):
        """Calcule les frais supplémentaires en temps réel depuis HotelChargeItem."""
        from django.db.models import Sum
        result = self.charges.aggregate(total=Sum('price', default=0))['total'] or 0
        # Multiply by quantity using Python sum for accuracy
        total = sum(c.quantity * c.price for c in self.charges.all())
        return total

    @property
    def total_amount(self):
        """Total hébergement + extras."""
        return self.amount_due + self.extra_charges

    @property
    def balance_due(self):
        """Reste à payer."""
        return self.total_amount - self.amount_paid

    @property
    def unique_ref(self):
        """Référence unique de la réservation hôtelière"""
        return f"RES-{str(self.id)[:8].upper()}"



class HotelChargeItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(HotelBooking, on_delete=models.CASCADE, related_name='charges')
    label = models.CharField(max_length=255, verbose_name="Libellé de la prestation (ex: Bière, Petit déj, Lessive)")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Prix unitaire (FCFA)")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        """Prix total = quantité × prix unitaire."""
        return self.quantity * self.price


class HotelShift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotel_shifts', verbose_name="Établissement")
    receptionist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receptionist_shifts', verbose_name="Réceptionniste")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="Date/Heure d'ouverture")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Date/Heure de clôture")
    initial_cash = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Fonds de caisse initial (FCFA)", validators=[MinValueValidator(0)])
    actual_cash = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="Espèces réelles comptées (FCFA)", validators=[MinValueValidator(0)])
    is_closed = models.BooleanField(default=False, verbose_name="Shift clôturé")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes / Observations de passation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Shift de Caisse"
        verbose_name_plural = "Shifts de Caisse"
        ordering = ['-start_time']

    def __str__(self):
        return f"Shift {self.receptionist.get_full_name()} du {self.start_time.strftime('%d/%m/%Y %H:%M')}"


class HotelPayment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(HotelBooking, on_delete=models.CASCADE, related_name='payments', verbose_name="Réservation")
    shift = models.ForeignKey(HotelShift, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', verbose_name="Shift de caisse")
    amount = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Montant (FCFA)", validators=[MinValueValidator(0)])
    payment_method = models.CharField(max_length=50, verbose_name="Mode de paiement")
    payment_type = models.CharField(max_length=50, choices=[('INITIAL', 'Initial'), ('CHARGE', 'Extra Charge'), ('FINAL', 'Final')], default='INITIAL')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Paiement Hôtelier"
        verbose_name_plural = "Paiements Hôteliers"
        ordering = ['-created_at']

    def __str__(self):
        return f"Pay: {self.amount} F - {self.payment_method} ({self.get_payment_type_display()})"


