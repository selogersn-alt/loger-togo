import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from django.conf import settings
settings.DEBUG = True

# You might need to adjust the host based on ALLOWED_HOSTS
c = Client(HTTP_HOST='agence.logertogo.local')

try:
    response = c.get('/deconnexion/')
    print("Status:", response.status_code)
    if response.status_code == 500:
        print(response.content.decode('utf-8'))
except Exception as e:
    print("Exception:", e)
