from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from management.models import HotelRoom, HotelBooking, HotelShift, HotelPayment
import datetime
from decimal import Decimal

User = get_user_model()

class HotelIntegrationTest(TestCase):
    urls = 'logertogo.urls_hotel'

    def hotel_reverse(self, name, *args, **kwargs):
        return reverse(name, *args, **kwargs, urlconf='logertogo.urls_hotel')

    def setUp(self):
        # 1. Create a hotel user
        self.hotel_user = User.objects.create_user(
            phone_number="78888888",
            password="testpassword123",
            role='HOTEL',
            company_name="Hotel Prestige"
        )
        self.hotel_user.is_saas_active = True
        self.hotel_user.save()

        # 2. Create room
        self.room = HotelRoom.objects.create(
            hotel=self.hotel_user,
            room_number="101",
            room_type="SINGLE",
            price_per_night=Decimal("45000.00"),
            price_per_hour=Decimal("10000.00"),
            status="AVAILABLE"
        )

        # 3. Test client
        self.client = Client()

    def test_hotel_booking_and_payment_flow(self):
        # Login
        self.client.login(phone_number="78888888", password="testpassword123")

        # 1. Open shift
        response = self.client.post(
            self.hotel_reverse('hotel_shift_open'),
            {'initial_cash': '10000.00'},
            HTTP_HOST='hotels.localhost'
        )
        self.assertEqual(response.status_code, 302)
        active_shift = HotelShift.objects.filter(hotel=self.hotel_user, is_closed=False).first()
        self.assertIsNotNone(active_shift)
        self.assertEqual(active_shift.initial_cash, Decimal('10000.00'))

        # 2. Create first booking (Initial cash payment)
        check_in = timezone.now() + datetime.timedelta(days=1)
        check_out = check_in + datetime.timedelta(days=2)
        check_in_str = check_in.strftime('%Y-%m-%dT%H:%M')
        check_out_str = check_out.strftime('%Y-%m-%dT%H:%M')

        booking_data = {
            'room_id': self.room.id,
            'client_name': 'Jean Dupont',
            'client_phone': '90000001',
            'check_in': check_in_str,
            'check_out': check_out_str,
            'rate_type': 'NIGHTLY',
            'amount_paid': '45000.00',
            'payment_method': 'ESPECES',
            'notes': 'Some notes'
        }

        response = self.client.post(
            self.hotel_reverse('hotel_booking_create'),
            booking_data,
            HTTP_HOST='hotels.localhost'
        )
        self.assertEqual(response.status_code, 302) # Redirect to booking detail

        # Verify booking created & amount calculated correctly
        booking = HotelBooking.objects.filter(client_name='Jean Dupont').first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.amount_due, Decimal('90000.00'))
        self.assertEqual(booking.amount_paid, Decimal('45000.00'))

        # Verify HotelPayment recorded
        payments = HotelPayment.objects.filter(booking=booking)
        self.assertEqual(payments.count(), 1)
        initial_pay = payments.first()
        self.assertEqual(initial_pay.amount, Decimal('45000.00'))
        self.assertEqual(initial_pay.payment_method, 'ESPECES')
        self.assertEqual(initial_pay.payment_type, 'INITIAL')

        # 3. Attempt double-booking overlapping with Dupont's booking
        overlap_data = {
            'room_id': self.room.id,
            'client_name': 'Paul Overlap',
            'client_phone': '90000002',
            'check_in': (check_in + datetime.timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M'),
            'check_out': (check_out - datetime.timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M'),
            'rate_type': 'NIGHTLY',
            'amount_paid': '0.00',
            'payment_method': 'ESPECES'
        }
        response = self.client.post(
            self.hotel_reverse('hotel_booking_create'),
            overlap_data,
            HTTP_HOST='hotels.localhost'
        )
        # Should redirect back since it's overlapping
        self.assertEqual(response.status_code, 302)
        overlap_booking = HotelBooking.objects.filter(client_name='Paul Overlap').first()
        self.assertIsNone(overlap_booking)

        # 4. Check out with final payment in WAVE
        # Verify that checkout adds to amount_paid and registers the WAVE payment,
        # but shifts expected cash should only aggregate the ESPECES payments!
        response = self.client.post(
            self.hotel_reverse('hotel_booking_checkout', args=[booking.id]),
            {'final_payment': '45000.00', 'payment_method_final': 'WAVE'},
            HTTP_HOST='hotels.localhost'
        )
        self.assertEqual(response.status_code, 302)

        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CHECKED_OUT')
        self.assertEqual(booking.amount_paid, Decimal('90000.00'))

        # Verify final payment recorded
        final_pay = HotelPayment.objects.filter(booking=booking, payment_type='FINAL').first()
        self.assertIsNotNone(final_pay)
        self.assertEqual(final_pay.amount, Decimal('45000.00'))
        self.assertEqual(final_pay.payment_method, 'WAVE')

        # 5. Add extra charges and verify guest folio / detail page renders successfully (Fixes 500 error on charge.total_price)
        from management.models import HotelChargeItem
        charge = HotelChargeItem.objects.create(
            booking=booking,
            label="Service de blanchisserie",
            quantity=2,
            price=Decimal("5000.00")
        )
        # Verify total_price works correctly and is a Decimal, not shadowed by Property
        self.assertEqual(charge.total_price, Decimal("10000.00"))

        # Access detail page
        response = self.client.get(
            self.hotel_reverse('hotel_booking_detail', args=[booking.id]),
            HTTP_HOST='hotels.localhost'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "blanchisserie")

        # 6. Access shifts dashboard and verify expected cash calculations
        response = self.client.get(
            self.hotel_reverse('hotel_shifts'),
            HTTP_HOST='hotels.localhost'
        )
        self.assertEqual(response.status_code, 200)
        # Caisse théorique attendue should be initial_cash (10000) + ESPECES payments (45000) = 55000 FCFA
        # WAVE payment (45000) is mobile money, so it shouldn't be in the physical cash drawer.
        self.assertEqual(response.context['expected_cash'], Decimal('55000.00'))
        print("[OK] Test d'intégration Caisse, Doubles Réservations & Folio validé avec succès !")
