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
                'publication_rent': 100.00,
                'publication_sale': 500.00,
                'publication_furnished': 300.00,
                'boost': 100.00,
                'popup': 500.00
            }
        return {
            'publication_rent': float(config.publication_fee_rent),
            'publication_sale': float(config.publication_fee_sale),
            'publication_furnished': float(config.publication_fee_furnished),
            'boost': float(config.boost_daily_fee),
            'popup': float(config.popup_daily_fee)
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
        Placeholder pour la génération du lien FedaPay.
        Retourne actuellement une URL de succès simulée pour l'assistance Admin.
        """
        # TODO: Implémenter l'appel API FedaPay ici plus tard
        # api_key = settings.FEDAPAY_API_KEY
        return f"/payments/callback/?ref={transaction.reference}&status=success"
