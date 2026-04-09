from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Property, PropertyImage, Transaction, PricingConfig, Favorite, PropertyEquipment

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
        queryset.update(is_published=True)
        self.message_user(request, f"{queryset.count()} annonce(s) ont été publiées.")

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
