import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logertogo.settings")
django.setup()

from django.test import RequestFactory
from logertogo.views import dashboard_view
from users.models import User

# Create a dummy user
user, _ = User.objects.get_or_create(phone_number='1234567890', role='TENANT')

request = RequestFactory().get('/mon-compte/')
request.user = user

try:
    response = dashboard_view(request)
    print("STATUS CODE:", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
