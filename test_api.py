import os
import django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logersenegal.settings")
django.setup()

c = Client()
response = c.get('/api/properties/')
print(f"Status code: {response.status_code}")
if response.status_code != 200:
    print(response.content.decode('utf-8'))
else:
    print("API returned 200 OK.")
