import paramiko
import sys

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

script_content = """import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logertogo.settings")
django.setup()

from logersn.models import Property

print(f"Total properties: {Property.objects.count()}")
print("\\n--- Last 10 Properties ---")
for p in Property.objects.all().order_by('-created_at')[:10]:
    print(f"[{p.id}] {p.title}")
    print(f"  Owner: {p.owner.email} ({p.owner.role})")
    print(f"  is_published: {p.is_published}")
    print(f"  visible_on_portal: {p.visible_on_portal}")
    print(f"  is_authorized_by_admin: {p.is_authorized_by_admin}")
    print(f"  publication_requested: {p.publication_requested}")
    print("-" * 30)
"""

def run_check():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=60)
        sftp = ssh.open_sftp()
        with sftp.file('/app/scratch_check.py', 'w') as f:
            f.write(script_content)
        sftp.close()
        
        stdin, stdout, stderr = ssh.exec_command('cd /app && docker compose exec -T web python scratch_check.py')
        print(stdout.read().decode('utf-8', 'replace'))
        err = stderr.read().decode('utf-8', 'replace')
        if err:
            print("ERRORS:", err)
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    run_check()
