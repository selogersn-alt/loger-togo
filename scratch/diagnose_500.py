import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("Connecting...")
try:
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
    print("Connected!")
    
    python_script = """
import os
import django
from django.test import Client
from django.urls import set_urlconf

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from users.models import User

# Find all hotel/auberge users and sub-agents
users = list(User.objects.filter(role__in=['HOTEL', 'AUBERGE']))
sub_agents = list(User.objects.filter(role='AGENT', parent_hotel__isnull=False))
all_users = users + sub_agents
print(f"Testing {len(users)} managers and {len(sub_agents)} sub-agents...")

client = Client()
set_urlconf('logertogo.urls_hotel')

for u in all_users:
    client.force_login(u)
    for path in ['/profil/', '/dashboard/']:
        try:
            response = client.get(path, HTTP_HOST='hotels.logertogo.com')
            print(f"User {u.phone_number} ({u.role}): GET {path} -> Status Code {response.status_code}")
            if response.status_code == 500:
                print("ERROR 500 DETECTED!")
        except Exception as e:
            import traceback
            print(f"EXCEPTION FOR USER {u.phone_number} on {path}:")
            print(traceback.format_exc())
"""

    cmd = "cd /app && docker compose exec -T web python manage.py shell"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.write(python_script)
    stdin.channel.shutdown_write()
    
    print("DIAGNOSIS STDOUT:")
    print(stdout.read().decode('utf-8', errors='replace'))
    err = stderr.read().decode('utf-8', errors='replace')
    if err:
        print("DIAGNOSIS STDERR:")
        print(err)
        
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
