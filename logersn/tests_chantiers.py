from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from logersn.models import Property
from management.models import Lease, RentPayment, PropertyInventory
import json

User = get_user_model()

class ChantiersIntegrationTest(TestCase):
    urls = 'logertogo.urls_agence'

    def agency_reverse(self, name, *args, **kwargs):
        return reverse(name, *args, **kwargs, urlconf='logertogo.urls_agence')

    def setUp(self):
        # 1. Création des comptes d'utilisateurs (avec is_saas_active = True pour l'agence)
        self.landlord = User.objects.create_user(
            phone_number="79055970", 
            password="Systernadjak@2026",
            first_name="NH",
            last_name="Immo",
            role=User.RoleEnum.AGENCY
        )
        self.landlord.is_saas_active = True
        self.landlord.save()
        
        self.tenant = User.objects.create_user(
            phone_number="90980053", 
            password="AkueMax@2022",
            first_name="Max",
            last_name="Akue"
        )
        
        # 2. Création du bien immobilier
        self.property = Property.objects.create(
            owner=self.landlord,
            title="Villa R+2 Chic Lomé",
            description="Villa d'élite à Lomé.",
            property_type="VILLA",
            price=250000.00,
            is_published=True,
            is_authorized_by_admin=True
        )
        
        # 3. Création du bail en attente de signature (PENDING)
        self.lease = Lease.objects.create(
            property=self.property,
            tenant=self.tenant,
            landlord=self.landlord,
            start_date=timezone.now().date(),
            rent_amount=250000.00,
            deposit_amount=500000.00,
            status=Lease.StatusEnum.PENDING,
            payment_due_day=5
        )
        
        # 4. Enregistrement d'un loyer pour le bail
        self.payment = RentPayment.objects.create(
            lease=self.lease,
            period_start=timezone.now().date(),
            period_end=timezone.now().date(),
            amount_due=250000.00,
            amount_paid=0.00,
            status=RentPayment.StatusEnum.UNPAID
        )
        
        # Client de test
        self.client = Client()

    def test_signature_otp_flow(self):
        """Vérifie le cycle complet de signature électronique par double validation OTP."""
        # Se connecter en tant que Bailleur/Agence
        self.client.login(phone_number="79055970", password="Systernadjak@2026")
        
        # 1. Demande d'OTP pour le bailleur
        response = self.client.get(self.agency_reverse('agency_lease_otp', args=[self.lease.id]), HTTP_HOST='agence.logertogo.com')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Re-fetch le bail pour obtenir l'OTP
        self.lease.refresh_from_db()
        landlord_otp = self.lease.landlord_otp
        self.assertIsNotNone(landlord_otp)
        
        # 2. Validation d'OTP pour le bailleur
        post_response = self.client.post(self.agency_reverse('agency_lease_sign', args=[self.lease.id]), {'otp_code': landlord_otp}, HTTP_HOST='agence.logertogo.com')
        self.assertEqual(post_response.status_code, 302) # Redirection après signature
        self.lease.refresh_from_db()
        self.assertTrue(self.lease.is_signed_by_landlord)
        
        # Se déconnecter puis se connecter en tant que Locataire
        self.client.logout()
        self.client.login(phone_number="90980053", password="AkueMax@2022")
        
        # 3. Demande d'OTP pour le locataire
        response = self.client.get(self.agency_reverse('agency_lease_otp', args=[self.lease.id]), HTTP_HOST='agence.logertogo.com')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        # Re-fetch le bail
        self.lease.refresh_from_db()
        tenant_otp = self.lease.tenant_otp
        self.assertIsNotNone(tenant_otp)
        
        # 4. Validation d'OTP pour le locataire
        post_response = self.client.post(self.agency_reverse('agency_lease_sign', args=[self.lease.id]), {'otp_code': tenant_otp}, HTTP_HOST='agence.logertogo.com')
        self.assertEqual(post_response.status_code, 302)
        
        # 5. Vérification du passage du bail à l'état ACTIF
        self.lease.refresh_from_db()
        self.assertTrue(self.lease.is_signed_by_tenant)
        self.assertEqual(self.lease.status, Lease.StatusEnum.ACTIVE)
        self.assertIsNotNone(self.lease.signed_at)
        print("[OK] Test d'intégration Signature OTP double-signataires validé avec succès !")

    def test_financial_analytics(self):
        """Vérifie la génération des indicateurs d'analyses financières de l'agence."""
        self.client.login(phone_number="79055970", password="Systernadjak@2026")
        
        response = self.client.get(self.agency_reverse('agency_financial_analysis'), HTTP_HOST='agence.logertogo.com')
        self.assertEqual(response.status_code, 200)
        
        # Vérification de la présence des variables d'analyses dans le contexte
        self.assertIn('total_due', response.context)
        self.assertIn('total_paid', response.context)
        self.assertIn('recovery_rate', response.context)
        self.assertIn('months_labels', response.context)
        self.assertEqual(response.context['total_due'], 250000.00)
        print("[OK] Test d'intégration Tableaux de Bord Financiers validé avec succès !")

    def test_property_inventory_crud(self):
        """Vérifie la création et l'impression d'un état des lieux."""
        self.client.login(phone_number="79055970", password="Systernadjak@2026")
        
        # 1. Création de l'état des lieux
        inv_data = {
            'inventory_type': 'IN',
            'inventory_date': timezone.now().date(),
            'general_condition': 'GOOD',
            'details_json': json.dumps([
                {"room": "Salon", "components": [{"name": "Sols", "condition": "GOOD", "comment": "RAS"}]}
            ]),
            'signature_agent': 'data:image/png;base64,agent_signature_sample_data',
            'signature_tenant': 'data:image/png;base64,tenant_signature_sample_data'
        }
        response = self.client.post(self.agency_reverse('agency_inventory_create', args=[self.lease.id]), inv_data, HTTP_HOST='agence.logertogo.com')
        self.assertEqual(response.status_code, 302) # Redirection après succès
        
        # 2. Vérification en base de données
        inventories = PropertyInventory.objects.filter(lease=self.lease)
        self.assertEqual(inventories.count(), 1)
        inv = inventories.first()
        self.assertEqual(inv.inventory_type, 'IN')
        self.assertEqual(inv.signature_agent, 'data:image/png;base64,agent_signature_sample_data')
        
        # 3. Accès au rapport d'état des lieux imprimable A4
        detail_response = self.client.get(self.agency_reverse('agency_inventory_detail', args=[inv.id]), HTTP_HOST='agence.logertogo.com')
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, "Salon")
        self.assertContains(detail_response, "Signature du Locataire")
        print("[OK] Test d'intégration État des Lieux & Rapport Tactile validé avec succès !")
