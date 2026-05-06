import requests
from django.conf import settings
from .models import PricingConfig, Transaction

class FedaPayBridge:
    """
    Pont d'intégration DigitalH pour le service de paiement FedaPay.
    Prêt pour la production. Nécessite les clés API FedaPay.
    """
    
    @staticmethod
    def get_pricing():
        config = PricingConfig.objects.first()
        if not config:
            return {
                'publication_rent': 0.0,
                'publication_sale': 0.0,
                'publication_furnished': 0.0,
                'boost': 1000.0,
                'popup': 5000.0
            }
        return {
            'publication_rent': float(config.publication_fee_rent),
            'publication_sale': float(config.publication_fee_sale),
            'publication_furnished': float(config.publication_fee_furnished),
            'boost': float(config.boost_daily_fee),
            'popup': float(config.boost_popup_fee)
        }

    @staticmethod
    def initiate_transaction(user, transaction_type, property_obj=None, days=1):
        """
        Calcule le montant et prépare la transaction en fonction de la catégorie du bien.
        """
        pricing = FedaPayBridge.get_pricing()
        amount = 0
        
        if transaction_type == 'PUBLICATION':
            if property_obj:
                cat = property_obj.listing_category
                if cat == 'RENT':
                    amount = pricing['publication_rent']
                elif cat == 'SALE':
                    amount = pricing['publication_sale']
                elif cat == 'FURNISHED':
                    amount = pricing['publication_furnished']
                else:
                    amount = pricing['publication_rent']
            else:
                amount = pricing['publication_rent']

        elif transaction_type == 'BOOST':
            amount = pricing['boost'] * days
        elif transaction_type == 'POPUP':
            amount = pricing['popup'] * days
            
        import uuid
        reference = f"LOGER-{uuid.uuid4().hex[:8].upper()}"
        
        transaction = Transaction.objects.create(
            user=user,
            property=property_obj,
            transaction_type=transaction_type,
            amount=amount,
            reference=reference,
            status='PENDING',
            days=days
        )
        
        return transaction

    @staticmethod
    def generate_payment_url(transaction):
        """
        Génère une URL vers la page de confirmation de demande de paiement (validation manuelle).
        """
        return f"/paiements/demande-envoyee/?ref={transaction.reference}"

def trigger_property_alerts(property_obj):
    """
    Recherche les alertes actives correspondant au bien et envoie les notifications.
    """
    from .models import PropertyAlert
    from logertogo.emails import send_new_property_alert
    from django.db.models import Q
    
    # Construction dynamique des filtres de matching
    filters = Q(is_active=True)
    
    # Matching Ville
    filters &= (Q(city=property_obj.city) | Q(city=''))
    
    # Matching Type de bien
    filters &= (Q(property_type=property_obj.property_type) | Q(property_type=''))
    
    # Matching Catégorie (Location/Vente)
    filters &= (Q(listing_category=property_obj.listing_category) | Q(listing_category=''))
    
    # Matching Budget (si budget max défini dans l'alerte)
    filters &= (Q(max_price__gte=property_obj.price) | Q(max_price__isnull=True))
    
    alerts = PropertyAlert.objects.filter(filters)
    subscriber_emails = list(alerts.values_list('email', flat=True).distinct())
    
    if subscriber_emails:
        return send_new_property_alert(subscriber_emails, property_obj)
    return 0
