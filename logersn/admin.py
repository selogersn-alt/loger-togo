from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import (
    Property, PropertyImage, Transaction, PricingConfig, Favorite, 
    PropertyEquipment, PropertyReview, PropertyAlert, Reservation, 
    PropertyAvailability, VisitRequest, MarketingCampaign, MarketingCampaignTemplate
)
from users.models import User
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from logertogo.emails import send_property_published_email

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        try:
            if obj.image_url:
                return format_html('<img src="{}" style="max-height: 100px; border-radius: 5px;" onerror="this.style.display=\'none\'" />', obj.image_url.url)
        except Exception:
            pass
        return "-"
    image_preview.short_description = "Aperçu"

class PropertyEquipmentInline(admin.TabularInline):
    model = PropertyEquipment
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('get_thumbnail', 'title', 'owner', 'listing_category', 'price', 'is_published', 'publication_requested', 'is_authorized_by_admin')
    list_filter = ('listing_category', 'property_type', 'is_published', 'publication_requested', 'is_authorized_by_admin', 'is_paid', 'is_boosted', 'is_featured_popup', 'city', 'created_at')
    search_fields = ('title', 'description', 'city', 'neighborhood')
    inlines = [PropertyImageInline, PropertyEquipmentInline]
    readonly_fields = ('discount_price',)
    fieldsets = (
        (_('Informations de base'), {'fields': ('title', 'owner', 'listing_category', 'property_type', 'city', 'neighborhood', 'description')}),
        (_('Tarification & Remises'), {'fields': ('price', 'discount_percentage', 'discount_price', 'price_per_night')}),
        (_('Statut & Visibilité'), {'fields': ('is_published', 'publication_requested', 'is_authorized_by_admin', 'is_paid', 'is_boosted', 'boost_until', 'is_featured_popup', 'popup_until')}),
    )
    actions = ['publish_properties', 'unpublish_properties', 'approve_publication', 'mark_as_paid', 'boost_selected']

    @admin.action(description="🔓 Approuver la publication publique")
    def approve_publication(self, request, queryset):
        queryset.update(is_authorized_by_admin=True, is_published=True)
        self.message_user(request, f"{queryset.count()} bien(s) approuvé(s) et publié(s) sur le portail public.")

    def get_thumbnail(self, obj):
        try:
            url = obj.get_main_image
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" onerror="this.src=\'https://via.placeholder.com/50\'" />', url)
        except Exception:
            return mark_safe('<div style="width: 50px; height: 50px; background: #eee; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #ccc;"><i class="fa fa-image"></i></div>')
    get_thumbnail.short_description = "Aperçu"

    @admin.action(description="✅ Publier les annonces sélectionnées")
    def publish_properties(self, request, queryset):
        count = 0
        alerts_sent = 0
        from logersn.utils import trigger_property_alerts
        
        for prop in queryset:
            if not prop.is_published:
                prop.is_published = True
                prop.save()
                if prop.owner and prop.owner.email:
                    send_property_published_email(prop.owner, prop)
                
                # Déclencher les alertes email aux abonnés
                alerts_sent += trigger_property_alerts(prop)
                count += 1
                
        self.message_user(request, f"{count} annonce(s) publiées, {alerts_sent} alerte(s) email envoyée(s).")

    @admin.action(description="❌ Retirer les annonces sélectionnées")
    def unpublish_properties(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, f"{queryset.count()} annonce(s) ont été retirées.")

    @admin.action(description="💰 Marquer comme payée")
    def mark_as_paid(self, request, queryset):
        queryset.update(is_paid=True)
        self.message_user(request, f"{queryset.count()} annonce(s) marquées comme payées.")

    @admin.action(description="🚀 Booster les annonces sélectionnées")
    def boost_selected(self, request, queryset):
        from django.utils import timezone
        import datetime
        queryset.update(is_boosted=True, boost_until=timezone.now() + datetime.timedelta(days=7))
        self.message_user(request, f"{queryset.count()} annonce(s) boostées pour 7 jours.")

@admin.register(PropertyEquipment)
class PropertyEquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'property', 'icon_class')
    list_filter = ('name', 'brand')
    search_fields = ('name', 'brand', 'property__title')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'transaction_type', 'amount', 'status', 'property_link', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('reference', 'user__phone_number', 'user__email')
    actions = ['validate_transactions']

    def property_link(self, obj):
        if obj.property:
            return format_html('<a href="{}">{}</a>', f"/admin/logersn/property/{obj.property.id}/change/", obj.property.title)
        return "-"
    property_link.short_description = "Bien concerné"

    @admin.action(description="✅ Valider manuellement les transactions (Activer Boost/Pub)")
    def validate_transactions(self, request, queryset):
        from django.utils import timezone
        import datetime
        count = 0
        for trans in queryset:
            if trans.status != 'SUCCESS':
                trans.status = 'SUCCESS'
                trans.save()
                
                # Appliquer l'effet du boost ou de la publication
                if trans.transaction_type == 'PUBLICATION' and trans.property:
                    trans.property.is_paid = True
                    trans.property.save()
                elif trans.transaction_type == 'BOOST' and trans.property:
                    trans.property.is_boosted = True
                    trans.property.boost_until = timezone.now() + datetime.timedelta(days=trans.days)
                    trans.property.save()
                count += 1
        self.message_user(request, f"{count} transaction(s) validée(s) et services activés.")

@admin.register(PricingConfig)
class PricingConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'publication_fee_rent', 'publication_fee_sale', 'publication_fee_furnished', 'boost_daily_fee', 'boost_popup_fee', 'boost_infeed_fee', 'boost_top_banner_fee')
    
    def has_add_permission(self, request):
        return not PricingConfig.objects.exists()

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'property', 'is_primary')
    list_filter = ('is_primary',)

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 5px;" />', obj.image_url.url)
        return "-"
    image_preview.short_description = "Aperçu"

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__phone_number', 'property__title')


@admin.register(PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ('property', 'reviewer', 'star_display', 'title', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('property__title', 'reviewer__email', 'reviewer__phone_number', 'comment')
    actions = ['approve_reviews', 'reject_reviews']
    readonly_fields = ('created_at',)

    def star_display(self, obj):
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="font-size:1.1rem;">{}</span>', stars)
    star_display.short_description = "Note"

    @admin.action(description="✅ Approuver et publier les avis sélectionnés")
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} avis approuvés et maintenant visibles sur le site.")

    @admin.action(description="❌ Masquer les avis sélectionnés")
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} avis masqués.")


@admin.register(PropertyAlert)
class PropertyAlertAdmin(admin.ModelAdmin):
    list_display = ('email', 'city', 'property_type', 'listing_category', 'max_price', 'is_active', 'created_at')
    list_filter = ('is_active', 'city', 'property_type', 'listing_category', 'created_at')
    search_fields = ('email', 'city')
    actions = ['deactivate_alerts', 'export_emails_csv']
    readonly_fields = ('token', 'created_at')

    @admin.action(description="🔕 Désactiver les alertes sélectionnées")
    def deactivate_alerts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} alertes désactivées.")

    @admin.action(description="📥 Exporter les emails (CSV)")
    def export_emails_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="alertes_emails.csv"'
        w = csv.writer(response)
        w.writerow(['Email', 'Ville', 'Type', 'Catégorie', 'Budget max', 'Actif', 'Date'])
        for alert in queryset:
            w.writerow([
                alert.email, alert.city, alert.property_type,
                alert.listing_category, alert.max_price or '',
                'Oui' if alert.is_active else 'Non',
                alert.created_at.strftime('%d/%m/%Y')
            ])
        return response
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'check_in', 'check_out', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('property__title', 'user__email')

@admin.register(VisitRequest)
class VisitRequestAdmin(admin.ModelAdmin):
    list_display = ('property', 'user', 'proposed_date', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('property__title', 'user__email')

@admin.register(PropertyAvailability)
class PropertyAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('property', 'start_date', 'end_date', 'is_available')
    list_filter = ('is_available',)

@admin.register(MarketingCampaignTemplate)
class MarketingCampaignTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject')
    search_fields = ('name', 'subject', 'content')

@admin.register(MarketingCampaign)
class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = ('subject', 'recipient_group', 'is_sent', 'scheduled_for', 'sent_at', 'created_at')
    list_filter = ('recipient_group', 'is_sent', 'scheduled_for', 'created_at')
    search_fields = ('subject', 'content')
    readonly_fields = ('is_sent', 'sent_at')
    filter_horizontal = ('individual_recipients',)
    actions = ['send_campaign_now']

    @admin.action(description="🚀 Envoyer MAINTENANT (Ignore la planification)")
    def send_campaign_now(self, request, queryset):
        from logertogo.emails import send_simple_email
        from django.utils import timezone
        
        for campaign in queryset:
            if campaign.is_sent:
                continue

            # Logique de récupération des utilisateurs (Groupes + Individuels)
            users = User.objects.filter(is_active=True).exclude(email__isnull=True).exclude(email='')
            
            if campaign.recipient_group == MarketingCampaign.RecipientGroup.AGENTS:
                users = users.filter(role='AGENT')
            elif campaign.recipient_group == MarketingCampaign.RecipientGroup.OWNERS:
                users = users.filter(role='OWNER')
            elif campaign.recipient_group == MarketingCampaign.RecipientGroup.TENANTS:
                users = users.filter(role='TENANT')
            elif campaign.recipient_group == MarketingCampaign.RecipientGroup.VERIFIED:
                users = users.filter(is_verified_pro=True)
            
            # Ajouter les destinataires individuels
            if campaign.individual_recipients.exists():
                users = (users | campaign.individual_recipients.all()).distinct()

            count = 0
            for user in users:
                first_name = user.first_name or "Client"
                last_name = user.last_name or ""
                html_content = campaign.content.replace('[PRENOM]', first_name).replace('[NOM]', last_name)
                
                # Utilisation de la fonction centralisée pour le design pro
                if send_simple_email(campaign.subject, html_content, user.email):
                    count += 1

            campaign.is_sent = True
            campaign.sent_at = timezone.now()
            campaign.save()

            self.message_user(request, f"🚀 Succès : Campagne '{campaign.subject}' envoyée à {count} utilisateurs.")

    class Media:
        js = ('js/admin_campaign_helper.js',)
