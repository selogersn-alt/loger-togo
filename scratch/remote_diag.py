import sys
sys.path.insert(0, '/app')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
import django
django.setup()

from django.test import RequestFactory
from users.models import User
from management.models import HotelBooking
import traceback

booking_ids = ['1a1a9345-1230-47b6-b646-3fffe6e05a8f', '3817dbe4-bd5a-4c90-adde-d071c9ae4f2a']

for bid in booking_ids:
    try:
        b = HotelBooking.objects.get(id=bid)
        hotel = b.room.hotel
        print(f"Testing booking {bid[:8]}... Hotel: {hotel}")
        
        from management.views_hotel import hotel_booking_detail
        rf = RequestFactory()
        request = rf.get(f'/reservations/{bid}/', HTTP_HOST='hotels.logertogo.com')
        request.user = hotel
        request.urlconf = 'logertogo.urls_hotel'
        
        try:
            response = hotel_booking_detail(request, booking_id=b.id)
            print(f"  Response status: {response.status_code}")
            if response.status_code == 200:
                print("  OK!")
            else:
                print(f"  Content: {response.content[:300]}")
        except Exception as e:
            print(f"  VIEW ERROR: {type(e).__name__}: {e}")
            traceback.print_exc()
    except HotelBooking.DoesNotExist:
        print(f"Booking {bid} not found")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        traceback.print_exc()
