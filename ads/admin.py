from django.contrib import admin
from .models import Advertisement, AdsConfig, SEOSetting

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'ad_type', 'location', 'is_active', 'created_at')
    list_filter = ('ad_type', 'location', 'is_active')
    search_fields = ('title', 'script_content')

@admin.register(AdsConfig)
class AdsConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not AdsConfig.objects.exists()

@admin.register(SEOSetting)
class SEOSettingAdmin(admin.ModelAdmin):
    list_display = ('title', 'meta_keywords')
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SEOSetting.objects.exists()
