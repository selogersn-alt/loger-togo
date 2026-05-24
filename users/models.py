import uuid
from django.db import models
from django.db.models import Avg, Sum, Count, Q
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, phone_number=None, password=None, **extra_fields):
        if not phone_number and not extra_fields.get('email'):
            raise ValueError('Vous devez fournir soit un numéro de téléphone, soit une adresse email.')
        
        # Normalisation de l'email
        if 'email' in extra_fields and extra_fields['email']:
            extra_fields['email'] = self.normalize_email(extra_fields['email'])
        else:
            extra_fields['email'] = None
            
        user = self.model(phone_number=phone_number or None, **extra_fields)
        user.set_password(password)
        
        # Génération d'un code OTP sécurisé à 6 chiffres
        import secrets
        user.phone_otp = str(secrets.SystemRandom().randint(100000, 999999))
        user.otp_created_at = timezone.now()
        
        user.is_phone_verified = True # Auto-verify phone since we abandoned SMS
        user.save(using=self._db)
        # Automatic send if email present
        if user.email:
            user.send_otp()
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class RoleEnum(models.TextChoices):
        TENANT = 'TENANT', _('Locataire')
        LANDLORD = 'LANDLORD', _('Bailleur')
        AGENCY = 'AGENCY', _('Agence Immobilière')
        BROKER = 'BROKER', _('Courtier')
        AGENT = 'AGENT', _('Agent')
        SUB_ADMIN = 'SUB_ADMIN', _('Sous-Administrateur DigitalH')
        CUSTOMER_SUPPORT = 'CUSTOMER_SUPPORT', _('Conseiller Client DigitalH')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True, db_index=True, verbose_name=_("Numéro de téléphone"))
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name=_("Adresse email"))
    company_name = models.CharField(max_length=150, null=True, blank=True, verbose_name=_("Nom de l'agence ou de l'entreprise"))
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True, verbose_name=_("Lien personnalisé"))
    coverage_area = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Zone de couverture"))
    class NotificationMode(models.TextChoices):
        SMS = 'SMS', _('SMS uniquement')
        EMAIL = 'EMAIL', _('E-mail uniquement')
        BOTH = 'BOTH', _('SMS & E-mail')

    role = models.CharField(max_length=20, choices=RoleEnum.choices, default=RoleEnum.TENANT, verbose_name=_("Statut du compte"))
    notification_preference = models.CharField(max_length=10, choices=NotificationMode.choices, default=NotificationMode.BOTH, verbose_name=_("Préférence de notification"))
    is_verified_pro = models.BooleanField(default=False, verbose_name=_("Professionnel Vérifié (Badge)"))
    
    profile_picture = models.FileField(upload_to='profile_pics/', null=True, blank=True, verbose_name=_("Photo de profil ou Logo"))
    is_phone_verified = models.BooleanField(default=False, verbose_name=_("Téléphone vérifié"))
    phone_otp = models.CharField(max_length=6, null=True, blank=True, verbose_name=_("Code OTP"))
    otp_created_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Date de génération de l'OTP"))
    first_name = models.CharField(max_length=150, null=True, blank=True, verbose_name=_("Prénom"))
    last_name = models.CharField(max_length=150, null=True, blank=True, verbose_name=_("Nom"))
    cni_number = models.CharField(max_length=50, null=True, blank=True, db_index=True, verbose_name=_("Numéro CNI / Passeport"))
    employer = models.CharField(max_length=150, null=True, blank=True, verbose_name=_("Employeur / Titre d'emploi"))
    marital_status = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Statut matrimonial"))
    spouse_name = models.CharField(max_length=150, null=True, blank=True, verbose_name=_("Nom de l'épouse/époux"))
    document_country = models.CharField(max_length=100, default='Togo', verbose_name=_("Pays de délivrance du document"))
    
    # Solvabilité (Lien avec NILS / Rentila)
    is_solvable = models.BooleanField(default=False, verbose_name=_("Locataire Solvable"))
    solvency_income_avg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    solvency_max_rent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    solvency_expiry_date = models.DateField(null=True, blank=True)
    
    # Identité Professionnelle
    years_of_experience = models.PositiveIntegerField(default=0, verbose_name=_("Années d'expérience"))
    bio = models.TextField(null=True, blank=True, verbose_name=_("Biographie / Description"))
    
    # Lien enfant-parent pour le SaaS Agence
    parent_agency = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='agency_tenants', verbose_name=_("Agence parente"))

    is_saas_active = models.BooleanField(default=False, verbose_name=_("Abonnement SaaS Agence Actif"))
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.get_full_name()} ({self.phone_number})"

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
            
            # SMS send via Termii (DEACTIVATED)
            # if self.notification_preference in ['SMS', 'BOTH']:
            #     from logertogo.sms import send_termii_sms
            #     message = f"Loger Togo: Votre code de vérification est {self.phone_otp}. Valable 10 min. Ne le partagez pas."
            #     send_termii_sms(self.phone_number, message)
                
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
                from io import BytesIO
                from django.core.files.base import ContentFile
                
                # Ouvrir l'image de manière sécurisée
                img = Image.open(self.profile_picture)
                
                if img.height > 500 or img.width > 500:
                    output_size = (500, 500)
                    img.thumbnail(output_size)
                    
                    # Sauvegarder dans un buffer
                    buffer = BytesIO()
                    img_format = img.format or 'JPEG'
                    img.save(buffer, format=img_format, quality=85)
                    buffer.seek(0)
                    
                    # Remplacer le fichier sans déclencher de boucle infinie
                    file_name = os.path.basename(self.profile_picture.name)
                    self.profile_picture.save(file_name, ContentFile(buffer.read()), save=False)
            except Exception:
                # On ignore l'erreur si le fichier est corrompu ou illisible
                pass


    @property
    def get_avatar_url(self):
        """Retourne l'URL de l'avatar : Photo de profil > Initiale du nom > Image par défaut."""
        if self.profile_picture:
            return self.profile_picture.url
        return f"https://ui-avatars.com/api/?name={self.get_short_name()}&background=0b4629&color=fff"

    @property
    def kyc_photo(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None

class KYCProfile(models.Model):
    class StatusEnum(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')

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






