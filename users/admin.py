from django.contrib import admin
from .models import User, KYCProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.utils.html import format_html
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = ('phone_number', 'first_name', 'last_name', 'role', 'phone_otp', 'is_phone_verified', 'is_verified_pro', 'is_active', 'is_staff')
    search_fields = ('email', 'phone_number', 'company_name', 'first_name', 'last_name', 'phone_otp')
    list_filter = ('role', 'is_verified_pro', 'is_active', 'is_staff', 'is_phone_verified')
    actions = [
        'verify_professionals', 'revoke_professionals', 'generate_recovery_code', 
        'send_otp_whatsapp', 'send_otp_email', 'generate_frontend_reset_link', 
        'send_reset_link_email', 'admin_set_temp_password', 'export_marketing_data',
        # 'send_templated_email', 
        'make_staff', 'revoke_staff',
    ]
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Informations de Connexion', {'fields': ('phone_number', 'email', 'password')}),
        ('Vérification & Sécurité', {'fields': ('phone_otp', 'is_phone_verified')}),
        ('Identité', {'fields': ('first_name', 'last_name', 'cni_number', 'profile_picture')}),
        ('Statut Professionnel', {'fields': ('role', 'is_verified_pro', 'company_name', 'coverage_area')}),
        ('Permissions Admin', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'email', 'password1', 'password2', 'role', 'company_name', 'coverage_area'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')

    @admin.action(description="⭐ Accorder droits d'accès Admin (is_staff)")
    def make_staff(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(request, f"{updated} utilisateur(s) ont maintenant accès à l'administration.")

    @admin.action(description="🚫 Révoquer droits d'accès Admin (is_staff)")
    def revoke_staff(self, request, queryset):
        updated = queryset.update(is_staff=False)
        self.message_user(request, f"Droits admin révoqués pour {updated} utilisateur(s).")

    @admin.action(description="🔗 Générer Lien de Réinitialisation Autonome WhatsApp")
    def generate_frontend_reset_link(self, request, queryset):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.urls import reverse
        
        for user in queryset:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm_public', kwargs={'uidb64': uid, 'token': token})
            )
            clean_phone = user.phone_number.replace('+', '').replace(' ', '').replace('-', '')
            wa_msg = f"Bonjour, pour réinitialiser votre mot de passe Loger Togo en toute autonomie, veuillez cliquer sur ce lien sécurisé : {reset_url}. L'équipe Loger Togo."
            wa_url = f"https://wa.me/{clean_phone}?text={wa_msg.replace(' ', '%20')}"
            
            self.message_user(request, format_html(
                'Lien de reset généré pour {}. <a href="{}" target="_blank" style="background-color: #25D366; color: white; padding: 5px 12px; border-radius: 5px; text-decoration: none; margin-left: 10px; font-weight: bold;"><i class="fa-brands fa-whatsapp"></i> Envoyer Lien WhatsApp</a>',
                user.phone_number, wa_url
            ))

    @admin.action(description="🔑 Générer un Code de Secours & Envoyer via WhatsApp")
    def generate_recovery_code(self, request, queryset):
        import random
        import string
        
        for user in queryset:
            temp_pass = ''.join(random.choices(string.digits, k=6))
            user.set_password(temp_pass)
            user.save()
            
            clean_phone = user.phone_number.replace('+', '').replace(' ', '').replace('-', '')
            wa_msg = f"Bonjour, voici votre nouveau code de connexion Loger Togo : {temp_pass}. Veuillez le changer dès votre connexion dans votre profil. Merci, l'équipe DigitalH."
            wa_url = f"https://wa.me/{clean_phone}?text={wa_msg.replace(' ', '%20')}"
            
            self.message_user(request, format_html(
                'Code de secours généré pour {}: <strong>{}</strong>. <a href="{}" target="_blank" style="background-color: #25D366; color: white; padding: 5px 12px; border-radius: 5px; text-decoration: none; margin-left: 10px; font-weight: bold;"><i class="fa-brands fa-whatsapp"></i> Envoyer via WhatsApp</a>',
                user.phone_number, temp_pass, wa_url
            ))

    @admin.action(description="📲 Envoyer le Code OTP actuel via WhatsApp")
    def send_otp_whatsapp(self, request, queryset):
        for user in queryset:
            if not user.phone_otp:
                import random
                user.phone_otp = str(random.randint(100000, 999999))
                user.save()
            
            clean_phone = user.phone_number.replace('+', '').replace(' ', '').replace('-', '')
            wa_msg = f"Bonjour, votre code de confirmation Loger Togo est : {user.phone_otp}. Merci de le saisir pour valider votre compte. L'équipe DigitalH."
            wa_url = f"https://wa.me/{clean_phone}?text={wa_msg.replace(' ', '%20')}"
            
            self.message_user(request, format_html(
                'Code OTP ({}) prêt pour {}. <a href="{}" target="_blank" style="background-color: #25D366; color: white; padding: 5px 12px; border-radius: 5px; text-decoration: none; margin-left: 10px; font-weight: bold;"><i class="fa-brands fa-whatsapp"></i> Envoyer le code</a>',
                user.phone_otp, user.phone_number, wa_url
            ))

    @admin.action(description="📩 Envoyer le Code OTP actuel via E-mail")
    def send_otp_email(self, request, queryset):
        count = 0
        for user in queryset:
            if user.email:
                if not user.phone_otp:
                    import random
                    user.phone_otp = str(random.randint(100000, 999999))
                    user.save()
                
                from logertogo.emails import send_otp_email
                send_otp_email(user, user.phone_otp)
                count += 1
            else:
                self.message_user(request, f"L'utilisateur {user.phone_number} n'a pas d'adresse e-mail.", level='warning')
        
        if count:
            self.message_user(request, f"{count} codes OTP envoyés par e-mail.")

    @admin.action(description="📧 Envoyer LIEN de réinitialisation par Email")
    def send_reset_link_email(self, request, queryset):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.urls import reverse
        from logertogo.emails import send_password_reset_email
        
        count = 0
        for user in queryset:
            if user.email:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = request.build_absolute_uri(
                    reverse('password_reset_confirm_public', kwargs={'uidb64': uid, 'token': token})
                )
                send_password_reset_email(user, reset_url)
                count += 1
            else:
                self.message_user(request, f"L'utilisateur {user.phone_number} n'a pas d'adresse e-mail.", level='warning')
        
        if count:
            self.message_user(request, f"{count} liens de réinitialisation envoyés par e-mail.")

    @admin.action(description="🔑 Définir MOT DE PASSE TEMPORAIRE (Admin choisit)")
    def admin_set_temp_password(self, request, queryset):
        import random
        import string
        
        temp_pass = "Loger" + "".join(random.choices(string.digits, k=4)) + "!"
        
        for user in queryset:
            user.set_password(temp_pass)
            user.save()
            
            clean_phone = user.phone_number.replace('+', '').replace(' ', '').replace('-', '')
            msg = f"Votre mot de passe temporaire Loger Togo est : {temp_pass}"
            wa_url = f"https://wa.me/{clean_phone}?text={msg.replace(' ', '%20')}"
            
            self.message_user(request, format_html(
                'Mot de passe défini pour {}: <strong>{}</strong>. <a href="{}" target="_blank" style="color: #25D366; font-weight: bold;">[Envoyer WhatsApp]</a>',
                user.phone_number, temp_pass, wa_url
            ))

    @admin.action(description="✅ Accorder le badge Professionnel Vérifié")
    def verify_professionals(self, request, queryset):
        updated = queryset.exclude(role='TENANT').update(is_verified_pro=True)
        self.message_user(request, f"{updated} professionnels ont été vérifiés avec succès.")

    @admin.action(description="❌ Révoquer le badge Professionnel")
    def revoke_professionals(self, request, queryset):
        updated = queryset.update(is_verified_pro=False)
        self.message_user(request, f"{updated} badges ont été révoqués.")

    @admin.action(description="📊 Exporter Données Marketing (CSV)")
    def export_marketing_data(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="marketing_logertogo_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'Telephone', 'Prenom', 'Nom', 'Role', 'Entreprise', 'Date Inscription'])
        
        for user in queryset:
            writer.writerow([
                user.email or '',
                user.phone_number,
                user.first_name,
                user.last_name,
                user.role,
                user.company_name or '',
                user.date_joined.strftime("%Y-%m-%d")
            ])
        
        return response

    @admin.action(description="📢 Envoyer un Modèle de Mail (Marketing)")
    def send_templated_email(self, request, queryset):
        # On convertit les UUID en string pour la session
        user_ids = [str(uid) for uid in queryset.values_list('id', flat=True)]
        request.session['selected_users_for_email'] = user_ids
        return HttpResponseRedirect(reverse_lazy('admin_select_email_template'))


@admin.register(KYCProfile)
class KYCProfileAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'cni_front_thumb', 'selfie_thumb', 'vision_api_status', 'verified_at')
    list_filter = ('vision_api_status', 'verified_at')
    search_fields = ('user__phone_number', 'user__first_name', 'user__last_name')
    actions = ['approve_kyc', 'reject_kyc']
    readonly_fields = ('verified_at', 'cni_front_preview', 'cni_back_preview', 'selfie_preview')
    
    fieldsets = (
        ('Utilisateur', {'fields': ('user', 'verified_at')}),
        ('Statut', {'fields': ('vision_api_status', 'rejection_reason')}),
        ('Documents d\'Identité', {
            'fields': (
                ('cni_front_image', 'cni_front_preview'),
                ('cni_back_image', 'cni_back_preview'),
                ('selfie_image', 'selfie_preview'),
            )
        }),
    )

    def user_link(self, obj):
        return format_html('<a href="{}">{}</a>', f"/admin/users/user/{obj.user.id}/change/", obj.user.get_full_name())
    user_link.short_description = "Utilisateur"

    def cni_front_thumb(self, obj):
        if obj.cni_front_image:
            return format_html('<img src="{}" style="width: 50px; height: 35px; object-fit: cover; border-radius: 4px;"/>', obj.cni_front_image.url)
        return "-"
    cni_front_thumb.short_description = "CNI (Recto)"

    def selfie_thumb(self, obj):
        if obj.selfie_image:
            return format_html('<img src="{}" style="width: 35px; height: 35px; object-fit: cover; border-radius: 50%;"/>', obj.selfie_image.url)
        return "-"
    selfie_thumb.short_description = "Selfie"

    def cni_front_preview(self, obj):
        if obj.cni_front_image:
            return format_html('<img src="{}" style="max-height: 300px; border-radius: 10px; border: 1px solid #ddd;"/>', obj.cni_front_image.url)
        return "Aucune image"
    cni_front_preview.short_description = "Aperçu CNI Recto"

    def cni_back_preview(self, obj):
        if obj.cni_back_image:
            return format_html('<img src="{}" style="max-height: 300px; border-radius: 10px; border: 1px solid #ddd;"/>', obj.cni_back_image.url)
        return "Aucune image"
    cni_back_preview.short_description = "Aperçu CNI Verso"

    def selfie_preview(self, obj):
        if obj.selfie_image:
            return format_html('<img src="{}" style="max-height: 300px; border-radius: 10px; border: 1px solid #ddd;"/>', obj.selfie_image.url)
        return "Aucune image"
    selfie_preview.short_description = "Aperçu Selfie"

    @admin.action(description="✅ Approuver et donner le Badge PRO")
    def approve_kyc(self, request, queryset):
        count = 0
        for profile in queryset:
            profile.vision_api_status = KYCProfile.StatusEnum.APPROVED
            profile.verified_at = timezone.now()
            profile.save()
            
            # Activer automatiquement le badge pro de l'utilisateur
            user = profile.user
            user.is_verified_pro = True
            user.save()
            count += 1
        self.message_user(request, f"{count} profil(s) KYC approuvés et badges PRO activés.")
            
    @admin.action(description="❌ Rejeter les profils KYC sélectionnés")
    def reject_kyc(self, request, queryset):
        updated = queryset.update(vision_api_status=KYCProfile.StatusEnum.REJECTED)
        self.message_user(request, f"{updated} profil(s) KYC rejetés.")







