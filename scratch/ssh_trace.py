import paramiko
import sys

def main():
    host = "157.180.127.70"
    port = 22
    username = "root"
    import os
    password = os.environ.get("VPS_PASSWORD")
    if not password:
        print("Error: VPS_PASSWORD environment variable is not set.")
        sys.exit(1)

    print("Connecting to VPS via SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, port=port, username=username, password=password, timeout=15)
        print("Connected!")
        
        python_code = """
import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logertogo.settings")
django.setup()

from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from management.views_agency import agency_login
from django.contrib.sessions.backends.db import SessionStore
import traceback

rf = RequestFactory()
req = rf.get('/connexion/')
req.META['HTTP_HOST'] = 'agence.logertogo.com'
req.urlconf = 'logertogo.urls_agence'
req.user = type('DummyUser', (), {'is_authenticated': False})()
req.session = SessionStore()
req._messages = FallbackStorage(req)

try:
    resp = agency_login(req)
    print('SUCCESS STATUS:', resp.status_code)
except Exception as e:
    print("EXCEPTION RAISED:")
    traceback.print_exc()
"""
        
        cmd = "docker compose -f /app/docker-compose.yml exec -T web python"
        print(f"Piping script into: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        # Write the python code into the stdin of the process
        stdin.write(python_code)
        stdin.flush()
        stdin.channel.shutdown_write()
        
        out_content = "".join(stdout.readlines())
        err_content = "".join(stderr.readlines())
        
        print("\n=== STDOUT ===")
        print(out_content)
        print("\n=== STDERR ===")
        print(err_content)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
