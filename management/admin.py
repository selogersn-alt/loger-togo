from django.contrib import admin
from .models import Lease, RentPayment, MaintenanceRequest, TenantDocument

@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'property', 'tenant', 'landlord', 'status', 'start_date')
    list_filter = ('status', 'start_date')
    search_fields = ('tenant__email', 'landlord__email', 'property__title')

@admin.register(RentPayment)
class RentPaymentAdmin(admin.ModelAdmin):
    list_display = ('lease', 'period_start', 'amount_due', 'amount_paid', 'status', 'date_paid')
    list_filter = ('status', 'date_paid')
    search_fields = ('lease__tenant__email',)

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'lease', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description')

@admin.register(TenantDocument)
class TenantDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'document_type')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    actions = ['verify_documents']

    def verify_documents(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_verified=True, verified_at=timezone.now())
    verify_documents.short_description = "Marquer comme vérifié par Loger Togo"
