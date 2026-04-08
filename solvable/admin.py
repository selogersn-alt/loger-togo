from django.contrib import admin
from django.utils import timezone
from .models import RentalFiliation, IncidentReport, PaymentHistory, PropertyApplication, ProfessionalFraudReport, PlatformPricing

@admin.register(RentalFiliation)
class RentalFiliationAdmin(admin.ModelAdmin):
    list_display = ('landlord', 'tenant', 'property', 'monthly_rent', 'status', 'start_date')
    list_filter = ('status',)
    search_fields = ('landlord__email', 'landlord__phone_number', 'tenant__email', 'tenant__phone_number')
    actions = ['terminate_filiation']

    @admin.action(description="Résilier les contrats sélectionnés")
    def terminate_filiation(self, request, queryset):
        # Mettre à jour le statut en TERMINATED et libérer la propriété si nécessaire
        for filiation in queryset:
            filiation.status = RentalFiliation.StatusEnum.TERMINATED
            filiation.end_date = timezone.now().date()
            filiation.save()
        self.message_user(request, "Contrats résiliés avec succès.")

@admin.register(IncidentReport)
class IncidentReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reported_tenant', 'amount_due', 'status', 'is_validated', 'is_contested', 'created_at')
    list_filter = ('status', 'is_validated', 'is_contested')
    search_fields = ('reporter__email', 'reported_tenant__email', 'contestation_reason')
    actions = ['mark_as_impacted', 'mark_as_resolved', 'reject_incident_after_dispute', 'send_vigilance_whatsapp', 'validate_incident']

    @admin.action(description="✅ VALIDER l'incident (Preuves vérifiées)")
    def validate_incident(self, request, queryset):
        updated = queryset.update(is_validated=True)
        self.message_user(request, f"{updated} incidents ont été officiellement validés.")

    @admin.action(description="📲 Envoyer Alerte Vigilance WhatsApp au Locataire")
    def send_vigilance_whatsapp(self, request, queryset):
        from django.utils.html import format_html
        
        for incident in queryset:
            tenant = incident.reported_tenant
            clean_phone = tenant.phone_number.replace('+', '').replace(' ', '').replace('-', '')
            amount = incident.amount_due
            
            wa_msg = f"Bonjour {tenant.first_name}, un incident de paiement ({incident.get_incident_type_display()}) a été pré-enregistré sur votre profil NILS pour un montant de {amount} FCFA. Vous avez 48h pour régulariser ou contester avant impact définitif sur votre score de solvabilité national. L'équipe Solvable."
            wa_url = f"https://wa.me/{clean_phone}?text={wa_msg.replace(' ', '%20')}"
            
            self.message_user(request, format_html(
                'Alerte prête pour {}. <a href="{}" target="_blank" style="background-color: #dc3545; color: white; padding: 5px 12px; border-radius: 5px; text-decoration: none; margin-left: 10px; font-weight: bold;"><i class="fa-brands fa-whatsapp"></i> Envoyer Alerte</a>',
                tenant.phone_number, wa_url
            ))

    @admin.action(description="Définit le litige comme IMPACTED (Pénalise le score NILS)")
    def mark_as_impacted(self, request, queryset):
        for incident in queryset:
            incident.status = IncidentReport.StatusEnum.IMPACTED
            incident.save()

    @admin.action(description="Marquer comme RESOLVED (Fin de médiation)")
    def mark_as_resolved(self, request, queryset):
        for incident in queryset:
            incident.status = IncidentReport.StatusEnum.RESOLVED
            incident.save()

    @admin.action(description="REJETER l'incident (Médiation : preuve du locataire valide)")
    def reject_incident_after_dispute(self, request, queryset):
        for incident in queryset:
            incident.status = IncidentReport.StatusEnum.RESOLVED
            # Logique pour redonner les points NILS si nécessaire (le signal NILS fait le calcul)
            incident.save()
            self.message_user(request, "Incident rejeté, le locataire n'est plus pénalisé.")

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('rental_filiation', 'month_year', 'status', 'is_contested', 'payment_date')
    list_filter = ('status', 'is_contested')
    search_fields = ('rental_filiation__tenant__email', 'contestation_reason')
    actions = ['mark_as_paid', 'reject_payment_after_dispute']

    @admin.action(description="Marquer comme PAYÉ (Bonus au score NILS)")
    def mark_as_paid(self, request, queryset):
        for payment in queryset:
            payment.status = PaymentHistory.StatusEnum.PAID
            payment.payment_date = timezone.now()
            payment.is_contested = False
            payment.save()

    @admin.action(description="DECLARER IMPAYÉ (Médiation : paiement invalide)")
    def reject_payment_after_dispute(self, request, queryset):
        for payment in queryset:
            payment.status = PaymentHistory.StatusEnum.UNPAID
            payment.is_contested = False
            payment.save()
            self.message_user(request, "Paiement invalidé après médiation.")

    def has_delete_permission(self, request, obj=None):
        # Sécurité financière et intégrité NILS : On ne supprime pas une trace de paiement.
        return False

@admin.register(PropertyApplication)
class PropertyApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'property', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('applicant__phone_number', 'applicant__email', 'property__title')

@admin.register(ProfessionalFraudReport)
class ProfessionalFraudReportAdmin(admin.ModelAdmin):
    list_display = ('reported_pro_name', 'reported_pro_phone', 'is_validated', 'is_critical_alert', 'created_at')
    list_filter = ('is_validated', 'is_critical_alert', 'created_at')
    search_fields = ('reported_pro_name', 'reported_pro_phone', 'fraud_description')
    actions = ['validate_fraud', 'mark_as_critical', 'unmark_critical', 'link_to_existing_user']
    
    @admin.action(description="✅ VALIDER le signalement de fraude")
    def validate_fraud(self, request, queryset):
        queryset.update(is_validated=True)
        self.message_user(request, "Signalements validés et visibles sur la liste noire.")
        
    @admin.action(description="🔥 Mettre en ALERTE CRITIQUE (Bande défilante)")
    def mark_as_critical(self, request, queryset):
        queryset.update(is_critical_alert=True, is_validated=True)
        self.message_user(request, "Alertes activées sur le bandeau défilant du site.")
        
    @admin.action(description="🧊 Retirer l'alerte critique")
    def unmark_critical(self, request, queryset):
        queryset.update(is_critical_alert=False)

    @admin.action(description="🔗 Tenter de lier aux comptes existants")
    def link_to_existing_user(self, request, queryset):
        from users.models import User
        count = 0
        for report in queryset:
            if report.reported_pro_phone:
                user = User.objects.filter(phone_number__icontains=report.reported_pro_phone).first()
                if user:
                    report.reported_user = user
                    report.save()
                    count += 1
        self.message_user(request, f"{count} signalements ont été liés à des comptes utilisateurs.")

@admin.register(PlatformPricing)
class PlatformPricingAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'price', 'is_active')
    list_editable = ('price', 'is_active')
