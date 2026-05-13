import os
import django
from django.test import RequestFactory
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logertogo.settings")
django.setup()

from logersn.views import near_me_view
from users.models import User

# Create a dummy user
user, _ = User.objects.get_or_create(phone_number='1234567890', role='TENANT')

rf = RequestFactory()

# Test cases
cases = [
    {'lat': '6.1311', 'lng': '1.2228'},
    {'lat': None, 'lng': None},
    {'lat': 'abc', 'lng': 'def'},
    {},
]

for case in cases:
    print(f"\nTesting with params: {case}")
    request = rf.get('/autour-de-moi/', case)
    request.user = user
    try:
        response = near_me_view(request)
        print("STATUS CODE:", response.status_code)
    except Exception as e:
        import traceback
        traceback.print_exc()
