from django.contrib import admin
from .models import Lease, RentPayment, MaintenanceRequest, TenantDocument, AgencyClient, ContractTemplate

class PrivateSaaSAdmin(admin.ModelAdmin):
    """
    Classe de base pour tous les modèles du SaaS Pro.
    Garantit une sécurité et un cloisonnement absolus en bloquant tout accès 
    (lecture, écriture, modification, suppression) depuis l'administration globale Django.
    Les données privées appartiennent exclusivement à chaque agence dans son environnement.
    """
    def has_module_permission(self, request):
        return False

    def has_view_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AgencyClient)
class AgencyClientAdmin(PrivateSaaSAdmin):
    list_display = ('full_name', 'phone', 'email', 'agency', 'client_type', 'status', 'pipeline_stage', 'created_at')
    list_filter = ('client_type', 'status', 'pipeline_stage')
    search_fields = ('full_name', 'phone', 'email', 'agency__phone_number', 'agency__email')


@admin.register(Lease)
class LeaseAdmin(PrivateSaaSAdmin):
    list_display = ('id', 'property', 'tenant', 'landlord', 'status', 'start_date')
    list_filter = ('status', 'start_date')
    search_fields = ('tenant__email', 'landlord__email', 'property__title')


@admin.register(RentPayment)
class RentPaymentAdmin(PrivateSaaSAdmin):
    list_display = ('lease', 'period_start', 'amount_due', 'amount_paid', 'status', 'date_paid')
    list_filter = ('status', 'date_paid')
    search_fields = ('lease__tenant__email',)


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(PrivateSaaSAdmin):
    list_display = ('title', 'lease', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description')


@admin.register(TenantDocument)
class TenantDocumentAdmin(PrivateSaaSAdmin):
    list_display = ('user', 'document_type', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'document_type')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    actions = ['verify_documents']

    def verify_documents(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_verified=True, verified_at=timezone.now())
    verify_documents.short_description = "Marquer comme vérifié par Loger Togo"


@admin.register(ContractTemplate)
class ContractTemplateAdmin(PrivateSaaSAdmin):
    list_display = ('title', 'agency', 'created_at')
    search_fields = ('title', 'agency__phone_number', 'agency__email')
