import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

script = """import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()
from logersn.models import Property
print('--- RECENT PROPERTIES ---')
for p in Property.objects.order_by('-created_at')[:5]:
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
    with sftp.file('/app/check_db.py', 'w') as f:
        f.write(script)
    sftp.close()
    
    stdin, stdout, stderr = ssh.exec_command('cd /app && docker compose exec -T web python check_db.py')
    print("STDOUT:")
    print(stdout.read().decode())
    print("STDERR:")
    print(stderr.read().decode())
    ssh.close()

if __name__ == '__main__':
    run()
