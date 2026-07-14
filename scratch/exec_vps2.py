import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

script = """import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()
from logersn.models import Property
from django.utils import timezone
import datetime

today = timezone.now().date()
print(f'--- PROPERTIES CREATED TODAY ({today}) ---')
props = Property.objects.filter(created_at__date=today).order_by('-created_at')
if not props.exists():
    print("NO properties created today.")
for p in props:
    print(f"ID: {p.id}")
    print(f"Title: {p.title}")
    print(f"Owner: {p.owner.email} (Role: {p.owner.role})")
    print(f"Is Published: {p.is_published}")
    print(f"Visible on Portal: {p.visible_on_portal}")
    print(f"Authorized: {p.is_authorized_by_admin}")
    print(f"Publication Req: {p.publication_requested}")
    print('---')
"""

def run():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD)
    sftp = ssh.open_sftp()
    with sftp.file('/app/check_db2.py', 'w') as f:
        f.write(script)
    sftp.close()
    
    stdin, stdout, stderr = ssh.exec_command('cd /app && docker compose exec -T web python check_db2.py')
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    
    with open('db_check_result.txt', 'w') as f:
        f.write(out + "\n" + err)
    
    print("Check completed, results saved to db_check_result.txt.")
    ssh.close()

if __name__ == '__main__':
    run()
