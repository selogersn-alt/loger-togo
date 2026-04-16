from .models import ProfessionalFraudReport, SystemAlert

def fraud_alerts_processor(request):
    """Injecte les alertes critiques de fraude dans le bandeau défilant."""
    try:
        alerts = ProfessionalFraudReport.objects.filter(is_validated=True, is_critical_alert=True).order_by('-created_at')[:5]
    except Exception:
        alerts = []
    return {
        'critical_fraud_alerts': alerts
    }

def system_alerts_processor(request):
    """Injecte les alertes système actives (Urgence, Info, etc.) dans toutes les pages."""
    try:
        active_alerts = SystemAlert.objects.filter(is_active=True).order_by('-created_at')
    except Exception:
        active_alerts = []
    return {
        'active_system_alerts': active_alerts
    }
