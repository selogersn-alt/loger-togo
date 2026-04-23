import os
import django
from django.test import Client

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logertogo.settings")
django.setup()

client = Client(HTTP_HOST="logertg.com")
try:
    response = client.get("/")
    print("Home status:", response.status_code)
    if response.status_code == 500:
        print(response.content)
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    response = client.get("/annonces/")
    print("Annonces status:", response.status_code)
    if response.status_code == 500:
        print(response.content)
except Exception as e:
    import traceback
    traceback.print_exc()
