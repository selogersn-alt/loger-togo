import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from django.conf import settings
settings.DEBUG = True

c = Client(HTTP_HOST='agence.logertogo.local')
response = c.get('/explications/')
print(f"Status: {response.status_code}")
if response.status_code == 500:
    print("500 ERROR CAUGHT")
