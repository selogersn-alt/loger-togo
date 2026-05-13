from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Property, Transaction, PricingConfig
from .utils import FedaPayBridge
import uuid

User = get_user_model()

class DigitalHMonetizationTest(TestCase):
    def setUp(self):
        # Création de l'environnement de test
        self.user = User.objects.create_user(phone_number="770000000", password="testpassword123")
        self.pricing = PricingConfig.objects.create(
            publication_fee_rent=100.00,
            publication_fee_sale=100.00,
            publication_fee_furnished=100.00,
            boost_daily_fee=100.00,
            boost_popup_fee=500.00
        )
        self.property = Property.objects.create(
            owner=self.user,
            title="Villa Test DigitalH",
            description="Une villa de test pour la certification.",
            property_type="VILLA",
            price=500000.00,
            is_published=False,
            is_paid=False
        )

    def test_pricing_logic(self):
        """Vérifie que les tarifs DigitalH (100F/500F) sont respectés."""
        pricing = FedaPayBridge.get_pricing()
        self.assertEqual(pricing['publication_rent'], 100.00)
        self.assertEqual(pricing['publication_sale'], 100.00)
        self.assertEqual(pricing['publication_furnished'], 100.00)
        self.assertEqual(pricing['boost'], 100.00)
        self.assertEqual(pricing['popup'], 500.00)
        print("[OK] Certification Tarifs réussie : 100F/500F validés.")

    def test_transaction_initiation(self):
        """Vérifie la création correcte d'une transaction de publication."""
        transaction = FedaPayBridge.initiate_transaction(self.user, 'PUBLICATION', self.property)
        # Assumant que le prix de base pour cette propriété est publication_rent car elle a rent_price
        self.assertEqual(transaction.amount, 100.00)
        self.assertEqual(transaction.status, 'PENDING')
        self.assertTrue(transaction.reference.startswith('LOGER-'))
        print(f"[OK] Certification Transaction réussie : Référence {transaction.reference} générée.")

    def test_boost_logic(self):
        """Vérifie le calcul pour un boost de 3 jours (300F)."""
        transaction = FedaPayBridge.initiate_transaction(self.user, 'BOOST', self.property, days=3)
        self.assertEqual(transaction.amount, 300.00)
        print("[OK] Certification Boost (3j x 100F = 300F) réussie.")

    def test_popup_logic(self):
        """Vérifie le calcul pour un pop-up de 2 jours (1000F)."""
        transaction = FedaPayBridge.initiate_transaction(self.user, 'POPUP', self.property, days=2)
        self.assertEqual(transaction.amount, 1000.00)
        print("[OK] Certification Pop-up (2j x 500F = 1000F) réussie.")

    def test_payment_activation_simulated(self):
        """Vérifie que le paiement active correctement les drapeaux de visibilité."""
        # Simulation d'un succès de paiement via le bridge
        from django.test import Client
        c = Client()
        c.login(phone_number="770000000", password="testpassword123")
        
        transaction = FedaPayBridge.initiate_transaction(self.user, 'PUBLICATION', self.property)
        
        # Appel simulé au callback
        response = c.get(f'/paiement/callback/?ref={transaction.reference}&status=success')
        
        # Re-fetch property
        self.property.refresh_from_db()
        self.assertTrue(self.property.is_paid)
        print("[OK] Certification Flux de Paiement réussie : L'annonce est marquée comme PAYÉE.")
