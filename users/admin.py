from django.contrib import admin
from .models import User, KYCProfile, NILS_Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = ('phone_number', 'first_name', 'last_name', 'role', 'phone_otp', 'is_phone_verified', 'is_verified_pro', 'is_active')
    search_fields = ('email', 'phone_number', 'company_name', 'first_name', 'last_name', 'phone_otp')
    list_filter = ('role', 'is_verified_pro', 'is_active', 'is_staff', 'is_phone_verified')
    actions = ['verify_professionals', 'revoke_professionals', 'generate_recovery_code', 'send_otp_whatsapp']
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Informations de Connexion', {'fields': ('phone_number', 'email', 'password')}),
        ('Vérification & Sécurité', {'fields': ('phone_otp', 'is_phone_verified')}),
        ('Identité', {'fields': ('first_name', 'last_name', 'cni_number', 'profile_picture')}),
        ('Statut Professionnel', {'fields': ('role', 'is_verified_pro', 'company_name', 'coverage_area')}),
        ('Délégation : Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'password', 'password_confirm', 'role', 'company_name', 'coverage_area'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')

    @admin.action(description="🔑 Générer un Code de Secours & Envoyer via WhatsApp")
    def generate_recovery_code(self, request, queryset):
        import random
        import string
        from django.utils.html import format_html
        
        for user in queryset:
            # Génération d'un code robuste à 6 chiffres
            temp_pass = ''.join(random.choices(string.digits, k=6))
            user.set_password(temp_pass)
            user.save()
            
            # Préparation du lien WhatsApp de prestige DigitalH
            clean_phone = user.phone_number.replace('+', '').replace(' ', '').replace('-', '')
            wa_msg = f"Bonjour, voici votre nouveau code de connexion Logersenegal : {temp_pass}. Veuillez le changer dès votre connexion dans votre profil. Merci, l'équipe DigitalH."
            wa_url = f"https://wa.me/{clean_phone}?text={wa_msg.replace(' ', '%20')}"
            
            self.message_user(request, format_html(
                'Code de secours généré pour {}: <strong>{}</strong>. <a href="{}" target="_blank" style="background-color: #25D366; color: white; padding: 5px 12px; border-radius: 5px; text-decoration: none; margin-left: 10px; font-weight: bold;"><i class="fa-brands fa-whatsapp"></i> Envoyer via WhatsApp</a>',
                user.phone_number, temp_pass, wa_url
            ))

    @admin.action(description="📲 Envoyer le Code OTP actuel via WhatsApp")
    def send_otp_whatsapp(self, request, queryset):
        from django.utils.html import format_html
        
        for user in queryset:
            if not user.phone_otp:
                import random
                user.phone_otp = str(random.randint(100000, 999999))
                user.save()
            
            clean_phone = user.phone_number.replace('+', '').replace(' ', '').replace('-', '')
            wa_msg = f"Bonjour, votre code de confirmation Logersenegal est : {user.phone_otp}. Merci de le saisir pour valider votre compte. L'équipe DigitalH."
            wa_url = f"https://wa.me/{clean_phone}?text={wa_msg.replace(' ', '%20')}"
            
            self.message_user(request, format_html(
                'Code OTP ({}) prêt pour {}. <a href="{}" target="_blank" style="background-color: #25D366; color: white; padding: 5px 12px; border-radius: 5px; text-decoration: none; margin-left: 10px; font-weight: bold;"><i class="fa-brands fa-whatsapp"></i> Envoyer le code</a>',
                user.phone_otp, user.phone_number, wa_url
            ))

    @admin.action(description="Accorder le badge de Professionnel Vérifié")
    def verify_professionals(self, request, queryset):
        # We only verify non-tenants
        updated = queryset.exclude(role='TENANT').update(is_verified_pro=True)
        self.message_user(request, f"{updated} professionnels ont été vérifiés avec succès.")

    @admin.action(description="Révoquer le badge de Professionnel")
    def revoke_professionals(self, request, queryset):
        updated = queryset.update(is_verified_pro=False)
        self.message_user(request, f"{updated} badges ont été révoqués.")

from django.utils import timezone

@admin.register(KYCProfile)
class KYCProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'vision_api_status', 'verified_at')
    list_filter = ('vision_api_status',)
    actions = ['approve_kyc', 'reject_kyc']
    readonly_fields = ('cni_front_preview', 'cni_back_preview', 'selfie_preview')

    def cni_front_preview(self, obj):
        from django.utils.html import format_html
        if obj.cni_front_image:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.cni_front_image.url)
        return "Aucune image"
    cni_front_preview.short_description = "CNI Recto"

    def cni_back_preview(self, obj):
        from django.utils.html import format_html
        if obj.cni_back_image:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.cni_back_image.url)
        return "Aucune image"
    cni_back_preview.short_description = "CNI Verso"

    def selfie_preview(self, obj):
        from django.utils.html import format_html
        if obj.selfie_image:
            return format_html('<img src="{}" style="max-height: 200px;"/>', obj.selfie_image.url)
        return "Aucune image"
    selfie_preview.short_description = "Selfie"

    @admin.action(description="Approuver les profils KYC sélectionnés (Génère le NILS)")
    def approve_kyc(self, request, queryset):
        for profile in queryset:
            profile.vision_api_status = KYCProfile.StatusEnum.APPROVED
            profile.verified_at = timezone.now()
            profile.save() # Le .save() déclenche le signal !
            
    @admin.action(description="Rejeter les profils KYC sélectionnés")
    def reject_kyc(self, request, queryset):
        for profile in queryset:
            profile.vision_api_status = KYCProfile.StatusEnum.REJECTED
            profile.save()

from django.utils.html import format_html
from .models import User, KYCProfile, NILS_Profile, SearchLog

@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'searcher', 'query', 'results_found', 'ip_address')
    list_filter = ('timestamp', 'searcher')
    search_fields = ('query', 'ip_address')
    readonly_fields = ('timestamp', 'searcher', 'query', 'results_found', 'ip_address')

@admin.register(NILS_Profile)
class NILS_ProfileAdmin(admin.ModelAdmin):
    list_display = ('nils_number', 'user', 'reputation_badge', 'score')
    search_fields = ('nils_number', 'user__email', 'user__phone_number')
    list_filter = ('reputation_status',)

    def reputation_badge(self, obj):
        colors = {
            'GREEN': ('#28a745', 'Excellent'),
            'YELLOW': ('#ffc107', 'Moyen (Attention)'),
            'RED': ('#dc3545', 'Critique (Dépôt Plainte)')
        }
        color, label = colors.get(obj.reputation_status, ('#6c757d', 'Inconnu'))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">{}</span>',
            color, label
        )
    reputation_badge.short_description = "Réputation"
