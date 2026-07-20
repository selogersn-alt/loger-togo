import paramiko

def main():
    host = "157.180.127.70"
    username = 'root'
    password = 'AkueMax@2022'

    print("Connexion au serveur SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=30)

    # 1. Écrire le script de diagnostic multi-ligne sur l'hôte temporaire
    diag_script = """import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.test import RequestFactory
from logertogo.views import home_view

try:
    rf = RequestFactory()
    req = rf.get('/')
    res = home_view(req)
    print("STATUS CODE:", res.status_code)
except Exception as e:
    import traceback
    print("=== EXCEPTION TRACEBACK ===")
    traceback.print_exc()
"""

    sftp = ssh.open_sftp()
    remote_tmp = "/tmp/diag_500.py"
    with sftp.file(remote_tmp, "w") as f:
        f.write(diag_script)
    sftp.close()

    print("Injection du script de diagnostic dans le conteneur...")
    ssh.exec_command(f"docker cp {remote_tmp} app-web-1:/app/diag_500.py")

    print("Exécution du diagnostic...")
    stdin, stdout, stderr = ssh.exec_command("docker compose -f /app/docker-compose.yml exec -T web python /app/diag_500.py")
    
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    
    if out:
        print("STDOUT:")
        print(out)
    if err:
        print("STDERR:")
        print(err)

    # Nettoyage
    ssh.exec_command(f"rm -f {remote_tmp}")
    ssh.exec_command("docker compose -f /app/docker-compose.yml exec -T web rm -f /app/diag_500.py")
    
    ssh.close()

if __name__ == "__main__":
    main()
