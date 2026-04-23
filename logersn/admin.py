from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Property, PropertyImage, Transaction, PricingConfig, Favorite, PropertyEquipment, PropertyReview, PropertyAlert
from logertogo.emails import send_property_published_email

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-height: 100px; border-radius: 5px;" />', obj.image_url.url)
        return "-"
    image_preview.short_description = "Aperçu"

class PropertyEquipmentInline(admin.TabularInline):
    model = PropertyEquipment
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('get_thumbnail', 'title', 'owner', 'listing_category', 'price', 'is_paid', 'is_boosted', 'is_published')
    list_filter = ('listing_category', 'property_type', 'is_published', 'is_paid', 'is_boosted', 'is_featured_popup', 'city', 'created_at')
    search_fields = ('title', 'description', 'city', 'neighborhood')
    inlines = [PropertyImageInline, PropertyEquipmentInline]
    actions = ['publish_properties', 'unpublish_properties', 'mark_as_paid', 'boost_selected']

    def get_thumbnail(self, obj):
        first_img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if first_img and first_img.image_url:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />', first_img.image_url.url)
        return mark_safe('<div style="width: 50px; height: 50px; background: #eee; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #ccc;"><i class="fa fa-image"></i></div>')
    get_thumbnail.short_description = "Aperçu"

    @admin.action(description="✅ Publier les annonces sélectionnées")
    def publish_properties(self, request, queryset):
        count = 0
        alerts_sent = 0
        from logertogo.views import trigger_property_alerts
        
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
    list_display = ('reference', 'user', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('reference', 'user__phone_number', 'user__email')

@admin.register(PricingConfig)
class PricingConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'publication_fee_rent', 'publication_fee_sale', 'publication_fee_furnished', 'boost_daily_fee', 'popup_daily_fee')
    
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
