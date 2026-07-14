import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("Connecting to VPS...")
try:
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
    print("Connected successfully!")
    
    python_script = """
import os
import django
from django.test import Client
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from logersn.models import Property

print("1. Checking database counts...")
total_props = Property.objects.count()
visible_props = Property.objects.filter(is_published=True, visible_on_portal=True).count()
hotels_auberges = Property.objects.filter(property_type__in=['HOTEL', 'AUBERGE', 'CHAMBRE']).count()

print(f"   Total properties in DB: {total_props}")
print(f"   Published and visible on portal: {visible_props}")
print(f"   Properties with type HOTEL/AUBERGE/CHAMBRE: {hotels_auberges}")

client = Client()

print("\\n2. Testing GET /autour-de-moi/ on logertogo.com...")
response = client.get('/autour-de-moi/', HTTP_HOST='logertogo.com')
print(f"   Status code: {response.status_code}")
if response.status_code == 200:
    print("   Page loaded successfully!")
else:
    print("   Error page returned!")

print("\\n3. Testing GET /api/geo/nearby/ API...")
response_api = client.get('/api/geo/nearby/?lat=6.137&lng=1.222&radius=50', HTTP_HOST='logertogo.com')
print(f"   Status code: {response_api.status_code}")
if response_api.status_code == 200:
    data = json.loads(response_api.content.decode('utf-8'))
    results_list = data.get('results', [])
    print(f"   API successful! Returned {len(results_list)} nearby properties.")
    for idx, p in enumerate(results_list[:5]):
        print(f"   - Property {idx+1}: {p.get('title')} | Type: {p.get('type')} | Category: {p.get('category')} | Coordinates: ({p.get('lat')}, {p.get('lng')}) | Owner Role: {p.get('owner_role')}")
else:
    print("   API failed!")
"""

    cmd = "cd /app && docker compose exec -T web python manage.py shell"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write(python_script)
    stdin.channel.shutdown_write()
    
    print("\n=== RUNNING DIAGNOSTIC ON WEB CONTAINER ===")
    print(stdout.read().decode('utf-8', errors='replace'))
    err = stderr.read().decode('utf-8', errors='replace')
    if err:
        print("DIAGNOSIS ERRORS:")
        print(err)
        
except Exception as e:
    print(f"Connection Error: {e}")
finally:
    ssh.close()
