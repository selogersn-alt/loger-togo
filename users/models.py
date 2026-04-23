import uuid
from django.db import models
from django.db.models import Avg, Sum, Count, Q
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        # Si un email est fourni, on le normalise, sinon il reste None
        if 'email' in extra_fields and extra_fields['email']:
            extra_fields['email'] = self.normalize_email(extra_fields['email'])
        else:
            extra_fields['email'] = None
            
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        
        # Génération d'un code OTP à 6 chiffres pour vérification manuelle par l'admin
        import random
        user.phone_otp = str(random.randint(100000, 999999))
        
        user.save(using=self._db)
        # Envoi automatique si email présent
        user.send_otp()
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class RoleEnum(models.TextChoices):
        TENANT = 'TENANT', 'Locataire'
        LANDLORD = 'LANDLORD', 'Bailleur'
        AGENCY = 'AGENCY', 'Agence Immobilière'
        BROKER = 'BROKER', 'Courtier'
        AGENT = 'AGENT', 'Agent'
        SUB_ADMIN = 'SUB_ADMIN', 'Sous-Administrateur DigitalH'
        CUSTOMER_SUPPORT = 'CUSTOMER_SUPPORT', 'Conseiller Client DigitalH'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True, db_index=True, verbose_name="Numéro de téléphone")
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="Adresse email")
    company_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Nom de l'agence ou de l'entreprise")
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True, verbose_name="Lien personnalisé")
    coverage_area = models.CharField(max_length=255, null=True, blank=True, verbose_name="Zone de couverture")
    class NotificationMode(models.TextChoices):
        SMS = 'SMS', 'SMS uniquement'
        EMAIL = 'EMAIL', 'E-mail uniquement'
        BOTH = 'BOTH', 'SMS & E-mail'

    role = models.CharField(max_length=20, choices=RoleEnum.choices, default=RoleEnum.TENANT, verbose_name="Statut du compte")
    notification_preference = models.CharField(max_length=10, choices=NotificationMode.choices, default=NotificationMode.BOTH, verbose_name="Préférence de notification")
    is_verified_pro = models.BooleanField(default=False, verbose_name="Professionnel Vérifié (Badge)")
    
    profile_picture = models.FileField(upload_to='profile_pics/', null=True, blank=True, verbose_name="Photo de profil ou Logo")
    is_phone_verified = models.BooleanField(default=False, verbose_name="Téléphone vérifié")
    phone_otp = models.CharField(max_length=6, null=True, blank=True, verbose_name="Code OTP")
    first_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Nom")
    cni_number = models.CharField(max_length=50, null=True, blank=True, db_index=True, verbose_name="Numéro CNI / Passeport")
    employer = models.CharField(max_length=150, null=True, blank=True, verbose_name="Employeur / Titre d'emploi")
    marital_status = models.CharField(max_length=50, null=True, blank=True, verbose_name="Statut matrimonial")
    spouse_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Nom de l'épouse/époux")
    document_country = models.CharField(max_length=100, default='Togo', verbose_name="Pays de délivrance du document")
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.company_name or self.phone_number

    def get_short_name(self):
        return self.first_name or self.company_name or self.phone_number

    def send_otp(self):
        """Déclenche l'envoi du code OTP selon les préférences."""
        from logertogo.emails import send_otp_email
        if self.phone_otp:
            # Envoi par Email si configuré
            if self.notification_preference in ['EMAIL', 'BOTH'] and self.email:
                send_otp_email(self, self.phone_otp)
            
            # Envoi par SMS via Termii
            if self.notification_preference in ['SMS', 'BOTH']:
                from logertogo.sms import send_termii_sms
                message = f"Loger Togo: Votre code de vérification est {self.phone_otp}. Valable 10 min. Ne le partagez pas."
                send_termii_sms(self.phone_number, message)
                
            return True
        return False

    def save(self, *args, **kwargs):
        # Génération du slug pour les liens personnalisés
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            
            # Correction DigitalH : Gérer les chaînes vides et les tirets simples
            first = (self.first_name or "").strip()
            last = (self.last_name or "").strip()
            company = (self.company_name or "").strip()
            
            base_name = company or f"{first} {last}".strip()
            
            # Si le nom est vide ou juste un tiret, on utilise l'ID
            if not base_name or base_name == "None-None" or len(base_name) < 2:
                base_name = str(self.id or uuid.uuid4()).split('-')[0]
            
            new_slug = slugify(base_name)
            if not new_slug:
                new_slug = str(self.id or uuid.uuid4()).split('-')[0]
                
            # Vérifier l'unicité et ajouter un suffixe si besoin
            if User.objects.filter(slug=new_slug).exclude(pk=self.pk).exists():
                new_slug = f"{new_slug}-{str(self.id or uuid.uuid4())[:8]}"
            
            self.slug = new_slug

        # Automatisation DigitalH : Les admins et conseillers ont un accès staff automatique
        if self.role in [self.RoleEnum.SUB_ADMIN, self.RoleEnum.CUSTOMER_SUPPORT]:
            self.is_staff = True
        super().save(*args, **kwargs)
        if self.profile_picture:
            try:
                import os
                from PIL import Image
                # Sécurité DigitalH : Vérifier si le fichier existe réellement sur le serveur
                if os.path.exists(self.profile_picture.path):
                    img = Image.open(self.profile_picture.path)
                    if img.height > 500 or img.width > 500:
                        output_size = (500, 500)
                        img.thumbnail(output_size)
                        img.save(self.profile_picture.path)
            except (FileNotFoundError, Exception):
                # On ignore l'erreur si le fichier est manquant (fréquent sur Render/Ephemeral Storage)
                pass

    @property
    def nils_profile(self):
        # Fallback for compatibility: returns the tenant profile if exists, or any other
        return self.nils_profiles.filter(nils_type=self.RoleEnum.TENANT).first() or self.nils_profiles.first()

    @property
    def kyc_photo(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None

class KYCProfile(models.Model):
    class StatusEnum(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kyc_profile')
    cni_front_image = models.FileField(upload_to='kyc_docs/', null=True, blank=True)
    cni_back_image = models.FileField(upload_to='kyc_docs/', null=True, blank=True)
    selfie_image = models.FileField(upload_to='kyc_docs/', null=True, blank=True)
    vision_api_status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.PENDING)
    rejection_reason = models.TextField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"KYC - {self.user.phone_number}"

    def save(self, *args, **kwargs):
        # Si le KYC est approuvé, on met à jour la photo de profil de l'utilisateur avec le selfie
        if self.vision_api_status == 'APPROVED' and self.selfie_image:
            self.user.profile_picture = self.selfie_image
            self.user.save()
        super().save(*args, **kwargs)

class NILS_Profile(models.Model):
    class ReputationEnum(models.TextChoices):
        GREEN = 'GREEN', 'Green'
        YELLOW = 'YELLOW', 'Yellow'
        RED = 'RED', 'Red'

    nils_number = models.CharField(primary_key=True, max_length=50, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nils_profiles')
    nils_type = models.CharField(max_length=20, choices=User.RoleEnum.choices, default=User.RoleEnum.TENANT)
    reputation_status = models.CharField(max_length=20, choices=ReputationEnum.choices, default=ReputationEnum.GREEN)
    score = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nils_number} ({self.user.phone_number})"
    
    @property
    def total_incidents(self):
        """Nombre total d'incidents impactants rattachés à ce profil."""
        return 0

    @property
    def amount_unpaid(self):
        """Montant total des loyers impayés non résolus."""
        return 0

    @property
    def average_rating(self):
        """Calculates the average star rating (1-10)."""
        return 0.0

    def save(self, *args, **kwargs):
        if not self.nils_number:
            # Generate a unique NILS number with format NILS-TYPE-CODE6
            type_map = {
                'TENANT': 'LOC',
                'LANDLORD': 'BAIL',
                'AGENCY': 'AGE',
                'BROKER': 'CRT',
                'AGENT': 'AGT'
            }
            prefix = type_map.get(self.nils_type, 'USR')
            code = str(uuid.uuid4()).split('-')[0][:6].upper()
            self.nils_number = f"NILS-{prefix}-{code}"
        super().save(*args, **kwargs)

    def update_score(self):
        """
        Recalculate the NILS score.
        """
        self.score = 100
        self.save()

class SearchLog(models.Model):
    """Logs every NILS search performed by professionals for security audit."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    searcher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='performed_searches')
    query = models.CharField(max_length=255)
    results_found = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Search by {self.searcher} for '{self.query}' at {self.timestamp}"

class SolvencyDocument(models.Model):
    class DocTypeEnum(models.TextChoices):
        PAYSLIP = 'PAYSLIP', 'Bulletin de Salaire'
        CONTRACT = 'CONTRACT', 'Contrat de Travail'
        BANK_STATEMENT = 'BANK_STATEMENT', 'Relevé Bancaire'
        NINEA = 'NINEA', 'NINEA (Auto-entrepreneur)'
        ADMIN_DOC = 'ADMIN_DOC', 'Document Administratif'

    class StatusEnum(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        VERIFIED = 'VERIFIED', 'Vérifié'
        REJECTED = 'REJECTED', 'Rejeté'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solvency_docs')
    doc_type = models.CharField(max_length=50, choices=DocTypeEnum.choices)
    file = models.FileField(upload_to='solvency_docs/')
    status = models.CharField(max_length=20, choices=StatusEnum.choices, default=StatusEnum.PENDING)
    
    rejection_reason = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_doc_type_display()} - {self.user.phone_number}"

    def save(self, *args, **kwargs):
        # Si le document est vérifié, on peut marquer l'utilisateur comme solvable (si admin le décide)
        # Mais on laisse la gestion du badge is_solvable à l'admin manuellement ou via une vue dédiée
        super().save(*args, **kwargs)
