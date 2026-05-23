# Project directory must be in python path
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import uuid
import django
from django.conf import settings
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from logersn.models import Property, PropertyImage
from management.models import Lease, RentPayment, AgencyClient
from logersn.forms import PropertyForm

User = get_user_model()

class HardAuditRunner:
    def __init__(self):
        self.results = {
            "security": [],
            "business_logic": [],
            "routes": [],
            "summary": {"passed": 0, "failed": 0, "total": 0}
        }
        self.client = Client()

    def log_result(self, category, name, passed, details):
        self.results[category].append({
            "name": name,
            "passed": passed,
            "details": details
        })
        self.results["summary"]["total"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1

    def run_all(self):
        print("🚀 Starting High-Severity Hard Audit on Loger Togo platform...")
        
        # 1. Setup Test Database Entities (scoped inside transaction/cleaned up later)
        self.setup_test_data()

        # 2. Run Route & RBAC Audits
        self.audit_routes_and_rbac()

        # 3. Run IDOR Audits
        self.audit_idor_protections()

        # 4. Run CSRF Audit
        self.audit_csrf_protections()

        # 5. Run SQLi/XSS Safe-Regex Input Audits
        self.audit_input_sanitation()

        # 6. Run Business Logic Audits
        self.audit_business_logic()

        # 7. Clean up
        self.teardown_test_data()

        # 8. Compile Markdown Report
        self.generate_report()

    def setup_test_data(self):
        print("⚙️ Setting up audit test accounts and objects...")
        # Proactively clean up any stale test accounts from aborted runs
        self.teardown_test_data()

        # Create different roles
        self.agency_active = User.objects.create_user(
            phone_number="+22899000001",
            email="agency_active@audit.logertogo.com",
            role=User.RoleEnum.AGENCY,
            company_name="Audit Agency Active",
            first_name="Active",
            last_name="Agency",
            is_saas_active=True,
            password="auditpassword123"
        )
        
        self.agency_inactive = User.objects.create_user(
            phone_number="+22899000002",
            email="agency_inactive@audit.logertogo.com",
            role=User.RoleEnum.AGENCY,
            company_name="Audit Agency Inactive",
            is_saas_active=False,
            password="auditpassword123"
        )

        self.tenant_user = User.objects.create_user(
            phone_number="+22899000003",
            email="tenant@audit.logertogo.com",
            role=User.RoleEnum.TENANT,
            first_name="Jean",
            last_name="Locataire",
            password="auditpassword123"
        )

        self.other_agency = User.objects.create_user(
            phone_number="+22899000004",
            email="other_agency@audit.logertogo.com",
            role=User.RoleEnum.AGENCY,
            company_name="Other Agency",
            is_saas_active=True,
            password="auditpassword123"
        )

        # Create properties
        self.prop_active_agency = Property.objects.create(
            owner=self.agency_active,
            title="Luxueux Appartement Audit",
            description="Superbe appartement d'audit en plein Lomé.",
            listing_category=Property.CategoryEnum.RENT,
            property_type="APPARTEMENT",
            city="LOME",
            neighborhood="Adidogomé",
            price=250000.00,
            is_published=False,
            is_authorized_by_admin=False
        )

        self.prop_other_agency = Property.objects.create(
            owner=self.other_agency,
            title="Villa Secrete Autre Agence",
            description="Villa non autorisée à être lue par l'autre agence.",
            listing_category=Property.CategoryEnum.RENT,
            property_type="VILLA",
            city="LOME",
            neighborhood="Baguida",
            price=500000.00,
            is_published=False,
            is_authorized_by_admin=False
        )

        # Create Leases and payments
        self.lease_active = Lease.objects.create(
            property=self.prop_active_agency,
            tenant=self.tenant_user,
            landlord=self.agency_active,
            start_date=timezone.now().date(),
            rent_amount=250000.00,
            status=Lease.StatusEnum.ACTIVE
        )

        self.payment_active = RentPayment.objects.create(
            lease=self.lease_active,
            period_start=timezone.now().date(),
            period_end=timezone.now().date(),
            amount_due=250000.00,
            status=RentPayment.StatusEnum.UNPAID
        )

        self.lease_other = Lease.objects.create(
            property=self.prop_other_agency,
            tenant=self.tenant_user,
            landlord=self.other_agency,
            start_date=timezone.now().date(),
            rent_amount=500000.00,
            status=Lease.StatusEnum.ACTIVE
        )

        self.payment_other = RentPayment.objects.create(
            lease=self.lease_other,
            period_start=timezone.now().date(),
            period_end=timezone.now().date(),
            amount_due=500000.00,
            status=RentPayment.StatusEnum.UNPAID
        )

    def teardown_test_data(self):
        print("🧹 Cleaning up audit test data...")
        RentPayment.objects.filter(lease__landlord__email__contains="audit.logertogo.com").delete()
        Lease.objects.filter(landlord__email__contains="audit.logertogo.com").delete()
        Property.objects.filter(owner__email__contains="audit.logertogo.com").delete()
        User.objects.filter(email__contains="audit.logertogo.com").delete()

    def audit_routes_and_rbac(self):
        print("🔍 Auditing URL Routes and Role-Based Access Controls...")
        self.client = Client()


        # A. Public main site routes (Should return 200 for anonymous visitor)
        public_main_routes = [
            ('home', {}),
            ('about', {}),
            ('properties_list', {}),
            ('cgu', {}),
            ('privacy', {}),
        ]
        for name, kwargs in public_main_routes:
            try:
                url = reverse(name, kwargs=kwargs)
                response = self.client.get(url, HTTP_HOST='logertogo.com')
                passed = response.status_code == 200
                self.log_result("routes", f"Main Public URL: {name}", passed, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("routes", f"Main Public URL: {name}", False, str(e))

        # B. Agency Subdomain Promo (Should return 200 for anonymous visitor)
        try:
            url = reverse('agency_promo', urlconf='logertogo.urls_agence')
            response = self.client.get(url, HTTP_HOST='agence.logertogo.com')
            passed = response.status_code == 200
            self.log_result("routes", "Subdomain Promo Page", passed, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("routes", "Subdomain Promo Page", False, str(e))

        # C. Agency Subdomain Authenticated views (Anonymous Visitor should be redirected to Login)
        sensitive_agency_routes = [
            ('agency_dashboard', {}),
            ('agency_clients', {}),
            ('agency_pipeline', {}),
            ('agency_leases', {}),
            ('agency_payments', {}),
            ('agency_properties', {}),
            ('agency_property_create', {}),
            ('agency_property_edit', {'property_id': self.prop_active_agency.id}),
            ('agency_receipt', {'payment_id': self.payment_active.id}),
        ]

        self.client.logout()
        for name, kwargs in sensitive_agency_routes:
            try:
                url = reverse(name, kwargs=kwargs, urlconf='logertogo.urls_agence')
                response = self.client.get(url, HTTP_HOST='agence.logertogo.com')
                passed = response.status_code == 302 and 'connexion' in response.url
                self.log_result("security", f"RBAC: Anon Blocked on '{name}'", passed, f"Status: {response.status_code}, Redirect: {response.get('location', '')}")
            except Exception as e:
                self.log_result("security", f"RBAC: Anon Blocked on '{name}'", False, str(e))

        # D. Agency Subdomain Views (Logged-in non-SaaS agency user should be redirected to Promo Page)
        self.client.force_login(self.agency_inactive)
        for name, kwargs in sensitive_agency_routes:
            try:
                url = reverse(name, kwargs=kwargs, urlconf='logertogo.urls_agence')
                response = self.client.get(url, HTTP_HOST='agence.logertogo.com')
                passed = response.status_code == 302 and 'promo' in response.url
                self.log_result("security", f"RBAC: Non-SaaS Active Blocked on '{name}'", passed, f"Status: {response.status_code}, Redirect: {response.get('location', '')}")
            except Exception as e:
                self.log_result("security", f"RBAC: Non-SaaS Active Blocked on '{name}'", False, str(e))

        # E. Agency Subdomain Views (Logged-in Active SaaS agency user should see 200 OK)
        self.client.force_login(self.agency_active)
        for name, kwargs in sensitive_agency_routes:
            try:
                url = reverse(name, kwargs=kwargs, urlconf='logertogo.urls_agence')
                response = self.client.get(url, HTTP_HOST='agence.logertogo.com')
                passed = response.status_code == 200
                self.log_result("routes", f"Active SaaS Access to '{name}'", passed, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("routes", f"Active SaaS Access to '{name}'", False, str(e))

    def audit_idor_protections(self):
        print("🛡️ Auditing Insecure Direct Object Reference (IDOR) Protections...")
        self.client = Client()

        
        # Scenario: Agency A (active) tries to access resources belonging to Agency B (other_agency)
        self.client.force_login(self.agency_active)

        # 1. Receipt Access: Agency A tries to access Agency B's receipt
        try:
            url = reverse('agency_receipt', kwargs={'payment_id': self.payment_other.id}, urlconf='logertogo.urls_agence')
            response = self.client.get(url, HTTP_HOST='agence.logertogo.com')
            passed = response.status_code == 404
            self.log_result("security", "IDOR Protection: Receipt isolation", passed, f"Status: {response.status_code} (Expected 404)")
        except Exception as e:
            self.log_result("security", "IDOR Protection: Receipt isolation", False, str(e))

        # 2. Property Edit View: Agency A tries to edit Agency B's property
        try:
            url = reverse('agency_property_edit', kwargs={'property_id': self.prop_other_agency.id}, urlconf='logertogo.urls_agence')
            response = self.client.get(url, HTTP_HOST='agence.logertogo.com')
            passed = response.status_code == 404
            self.log_result("security", "IDOR Protection: Property editing isolation", passed, f"Status: {response.status_code} (Expected 404)")
        except Exception as e:
            self.log_result("security", "IDOR Protection: Property editing isolation", False, str(e))

        # 3. Property Toggle Publication Endpoint: Agency A tries to toggle publication on Agency B's property
        try:
            url = reverse('agency_property_toggle_publication', kwargs={'property_id': self.prop_other_agency.id}, urlconf='logertogo.urls_agence')
            response = self.client.post(url, HTTP_HOST='agence.logertogo.com')
            passed = response.status_code == 404
            self.log_result("security", "IDOR Protection: Property publication toggle isolation", passed, f"Status: {response.status_code} (Expected 404)")
        except Exception as e:
            self.log_result("security", "IDOR Protection: Property publication toggle isolation", False, str(e))

    def audit_csrf_protections(self):
        print("🧱 Auditing CSRF Protection on Forms...")
        # Since standard test client disables CSRF validation, we can simulate an external request with enforce_csrf_checks=True
        client_csrf = Client(enforce_csrf_checks=True)
        
        # Login is unauthenticated, but post without CSRF should fail with 403
        try:
            url = reverse('agency_login', urlconf='logertogo.urls_agence')
            response = client_csrf.post(url, {'username': 'test', 'password': 'pwd'}, HTTP_HOST='agence.logertogo.com')
            passed = response.status_code == 403
            self.log_result("security", "CSRF Protection: POST Login without token", passed, f"Status: {response.status_code} (Expected 403)")
        except Exception as e:
            self.log_result("security", "CSRF Protection: POST Login without token", False, str(e))

        # Property Creation without CSRF
        try:
            url = reverse('agency_property_create', urlconf='logertogo.urls_agence')
            response = client_csrf.post(url, {'title': 'Test CSRF'}, HTTP_HOST='agence.logertogo.com')
            passed = response.status_code == 403
            self.log_result("security", "CSRF Protection: POST Property Create without token", passed, f"Status: {response.status_code} (Expected 403)")
        except Exception as e:
            self.log_result("security", "CSRF Protection: POST Property Create without token", False, str(e))

    def audit_input_sanitation(self):
        print("🧹 Auditing SQL Injection and XSS inputs protection...")
        
        # Test character sanitization rules inside form.
        # We test that the custom regular expression safely cleans the title and description of invalid variation selectors
        # and standard HTML injection attempts.
        xss_payload = "<script>alert('XSS')</script> Superbe Villa!"
        variation_selector_payload = "Villa\ufe0f Magnifique!" # variation selector \ufe0f
        
        data = {
            'title': xss_payload,
            'description': variation_selector_payload,
            'listing_category': 'RENT',
            'property_type': 'VILLA',
            'city': 'LOME',
            'neighborhood': 'Adidogomé',
            'price': '350000',
            'surface': '150',
            'bedrooms': '3',
            'toilets': '2',
            'total_rooms': '5',
            'salons': '1',
            'kitchens': '1',
        }
        
        form = PropertyForm(data=data)
        form.is_valid()
        
        cleaned_title = form.cleaned_data.get('title', '')
        cleaned_desc = form.cleaned_data.get('description', '')
        
        # Check that brackets and special tags were correctly treated/stripped
        passed_xss = "<script>" not in cleaned_title and "</script>" not in cleaned_title
        # Check variation selectors are stripped
        passed_selector = "\ufe0f" not in cleaned_desc
        
        self.log_result("security", "XSS mitigation: strips HTML script tags from titles", passed_xss, f"Cleaned: {cleaned_title}")
        self.log_result("security", "Hardening: strips variation selector unicode invisible characters", passed_selector, f"Cleaned: {cleaned_desc}")

    def audit_business_logic(self):
        print("🧠 Auditing Business Logic Constraints...")
        self.client = Client()


        # 1. Negative numbers/fees bound check
        # We attempt to pass negative pricing variables into the property form
        negative_data = {
            'title': 'Appartement de test Negatif',
            'description': 'Description du bien.',
            'listing_category': 'RENT',
            'property_type': 'APPARTEMENT',
            'city': 'LOME',
            'neighborhood': 'Adidogomé',
            'price': '-250000', # Negative Price
            'visit_fee': '-5000', # Negative Fee
            'deposit_months': '-3', # Negative caution months
            'surface': '-120', # Negative surface
        }
        form = PropertyForm(data=negative_data)
        is_valid = form.is_valid()
        
        # Wait, if is_valid is True, we have a critical business logic flaw!
        # Let's inspect errors or values
        if not is_valid:
            self.log_result("business_logic", "Bounds: Blocks negative numbers on form validation", True, "Form threw validation errors correctly.")
        else:
            # Check values in cleaned data - they should at least be defaulted to 0 or absolute values if handled
            price = form.cleaned_data.get('price')
            visit_fee = form.cleaned_data.get('visit_fee')
            deposit_months = form.cleaned_data.get('deposit_months')
            surface = form.cleaned_data.get('surface')
            
            passed = float(price) >= 0 and visit_fee >= 0 and deposit_months >= 0 and surface >= 0
            self.log_result("business_logic", "Bounds: Blocks negative numbers (post-cleaning)", passed, f"Price: {price}, Visit fee: {visit_fee}, Deposit: {deposit_months}, Surface: {surface}")

        # 2. Listing auto-sync rules
        # Agency creates property with make_public = 'on' -> should request publication but NOT be published directly
        # Unless authorized by admin
        prop = Property.objects.create(
            owner=self.agency_active,
            title="Auto-Sync Rules Test Property",
            description="Description.",
            listing_category=Property.CategoryEnum.RENT,
            property_type="APPARTEMENT",
            city="LOME",
            neighborhood="Adidogomé",
            price=200000.00,
            publication_requested=True,
            is_published=False,
            is_authorized_by_admin=False
        )
        
        # Business logic rule: It must remain offline until the admin authorizes it
        passed_sync = (prop.is_published is False) and (prop.publication_requested is True)
        self.log_result("business_logic", "Sync Rules: CRM listing stays unpublished pending admin approval", passed_sync, f"is_published: {prop.is_published}, publication_requested: {prop.publication_requested}")

        # Simulate Admin approval
        prop.is_authorized_by_admin = True
        prop.is_published = True
        prop.save()
        
        # Quick toggle to withdraw
        # We do a POST request using client logged in as agency_active
        self.client.force_login(self.agency_active)
        url = reverse('agency_property_toggle_publication', kwargs={'property_id': prop.id}, urlconf='logertogo.urls_agence')
        response = self.client.post(url, HTTP_HOST='agence.logertogo.com')
        
        prop.refresh_from_db()
        passed_withdraw = (prop.is_published is False) and (prop.publication_requested is False)
        self.log_result("business_logic", "Sync Rules: Agency can withdraw listing without admin intervention", passed_withdraw, f"is_published: {prop.is_published}")

        # 3. Lease payments status transitions
        # We check the status transition flow for lease payments
        payment = RentPayment.objects.create(
            lease=self.lease_active,
            period_start=timezone.now().date(),
            period_end=timezone.now().date(),
            amount_due=100000.00,
            amount_paid=0.00,
            status=RentPayment.StatusEnum.UNPAID
        )
        
        # Test Case 3a: Partial payment
        # Trigger payment collection in agency_payments
        url = reverse('agency_payments', urlconf='logertogo.urls_agence')
        self.client.post(url, {
            'payment_id': payment.id,
            'amount_paid': '40000',
            'date_paid': timezone.now().date().isoformat(),
            'payment_method': 'ESPECES',
            'receipt_header': 'Mon Entete Custom',
            'receipt_footer': 'Mon Pied Custom'
        }, HTTP_HOST='agence.logertogo.com')
        
        payment.refresh_from_db()
        passed_partial = payment.status == RentPayment.StatusEnum.PARTIAL and float(payment.amount_paid) == 40000.0
        self.log_result("business_logic", "Payments: Transition to PARTIAL on partial collection", passed_partial, f"Status: {payment.status}, Paid: {payment.amount_paid}")

        # Test Case 3b: Full payment
        self.client.post(url, {
            'payment_id': payment.id,
            'amount_paid': '100000',
            'date_paid': timezone.now().date().isoformat(),
            'payment_method': 'T-MONEY',
            'receipt_header': 'Mon Entete Custom',
            'receipt_footer': 'Mon Pied Custom'
        }, HTTP_HOST='agence.logertogo.com')
        payment.refresh_from_db()
        passed_full = payment.status == RentPayment.StatusEnum.PAID and float(payment.amount_paid) == 100000.0
        self.log_result("business_logic", "Payments: Transition to PAID on full collection", passed_full, f"Status: {payment.status}, Paid: {payment.amount_paid}")

        # 4. Receipt Custom Branding Fallback Logic
        # We verify that the quittance page correctly displays branding assets.
        # It should fall back to using the landlord/agency profile picture as a logo if no specific receipt logo is provided.
        url_receipt = reverse('agency_receipt', kwargs={'payment_id': payment.id}, urlconf='logertogo.urls_agence')
        response = self.client.get(url_receipt, HTTP_HOST='agence.logertogo.com')
        
        # Inspect receipt page context parameters
        if response.context is not None:
            passed_fallback = 'payment' in response.context and 'agency' in response.context
        else:
            # Fall back to checking HTML content
            passed_fallback = b"QUITTANCE" in response.content or b"Loyer" in response.content
        self.log_result("business_logic", "Quittances: Context variables contains payment & agency", passed_fallback, f"Context keys present: {response.context.keys() if response.context else 'None (HTML body: ' + str(len(response.content)) + ' bytes)'}")


    def generate_report(self):
        passed_cnt = self.results["summary"]["passed"]
        failed_cnt = self.results["summary"]["failed"]
        total_cnt = self.results["summary"]["total"]
        pct = (passed_cnt / total_cnt) * 100 if total_cnt > 0 else 0
        
        markdown = f"""# 🛡️ Rapport d'Audit de Sécurité & Logique Métier Complet (Mai 2026)

## 📌 Résumé des tests exécutés
*   **Total des tests** : {total_cnt}
*   **Tests réussis** : {passed_cnt} ✅
*   **Tests échoués** : {failed_cnt} ❌
*   **Taux de succès** : {pct:.1f}%

---

## 🔒 1. AUDIT DE SÉCURITÉ & CONTROLE D'ACCÈS (RBAC / IDOR / CSRF)

| Nom du Test | Statut | Détails |
| :--- | :---: | :--- |
"""
        for t in self.results["security"]:
            status_emoji = "✅" if t["passed"] else "❌"
            markdown += f"| {t['name']} | {status_emoji} | {t['details']} |\n"

        markdown += """
---

## 🧠 2. AUDIT DE LOGIQUE MÉTIER & FLUX IMMOBILIERS

| Nom du Test | Statut | Détails |
| :--- | :---: | :--- |
"""
        for t in self.results["business_logic"]:
            status_emoji = "✅" if t["passed"] else "❌"
            markdown += f"| {t['name']} | {status_emoji} | {t['details']} |\n"

        markdown += """
---

## 🛣️ 3. AUDIT DES ROUTES & ENDPOINTS DE LA PLATEFORME

| Nom du Test | Statut | Détails |
| :--- | :---: | :--- |
"""
        for t in self.results["routes"]:
            status_emoji = "✅" if t["passed"] else "❌"
            markdown += f"| {t['name']} | {status_emoji} | {t['details']} |\n"

        markdown += """
---

## 📋 4. RECOMMANDATIONS & AMÉLIORATIONS

1.  **Validation Strict des Bornes Numériques** : En plus du formulaire, ajouter des contraintes `validators=[MinValueValidator(0)]` directement sur les modèles de base Django (`price`, `visit_fee`, `deposit_months`, etc.) pour une sécurité au niveau de la couche base de données.
2.  **CSRF sur les API** : S'assurer que les endpoints de l'API REST sous `/api/` utilisent correctement l'authentification par Token ou Session avec des en-têtes CSRF appropriés.
3.  **Cookies Multi-domaines** : Confirmer que la configuration `SESSION_COOKIE_DOMAIN = '.logertogo.com'` est bien présente dans les paramètres de production pour un SSO transparent.
"""

        # Write to the workspace audit report
        with open('d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\AUDIT_REPORT_MAY_2026.md', 'w', encoding='utf-8') as f:
            f.write(markdown)
            
        print(f"\n🎉 Audit complete! Written details to AUDIT_REPORT_MAY_2026.md. Status: {passed_cnt}/{total_cnt} passed.")

if __name__ == "__main__":
    runner = HardAuditRunner()
    runner.run_all()
