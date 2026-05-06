from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    path('bailleur/', views.landlord_dashboard_view, name='landlord_dashboard'),
    path('locataire/', views.tenant_dashboard_view, name='tenant_dashboard'),
    path('bail/nouveau/', views.create_lease_view, name='create_lease'),
    path('bail/nouveau/<uuid:property_id>/', views.create_lease_view, name='create_lease_property'),
    path('bail/<uuid:lease_id>/paiement/', views.record_payment_view, name='record_lease_payment'),
    path('bail/<uuid:lease_id>/pdf/', views.download_lease_pdf_view, name='download_lease_pdf'),
    path('paiement/<uuid:payment_id>/pdf/', views.download_receipt_pdf_view, name='download_receipt_pdf'),
    path('incident/signaler/<uuid:lease_id>/', views.report_incident_view, name='report_incident'),
    path('incident/<uuid:incident_id>/maj/', views.update_incident_status_view, name='update_incident_status'),
    path('mon-dossier/', views.tenant_dossier_view, name='tenant_dossier'),
    path('dossier-locataire/<uuid:tenant_id>/', views.tenant_dossier_view_for_landlord, name='tenant_dossier_view_for_landlord'),
    path('relancer-impayes/', views.send_payment_reminders_view, name='send_payment_reminders'),
    path('export-comptabilite/', views.export_accounting_csv_view, name='export_accounting_csv'),
    path('candidature/<uuid:app_id>/statut/', views.update_application_status, name='update_application_status'),
    path('incident/<uuid:incident_id>/mediation/', views.mediation_room_view, name='mediation_room'),
]
