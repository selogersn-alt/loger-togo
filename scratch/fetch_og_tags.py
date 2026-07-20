import paramiko

def main():
    host = "157.180.127.70"
    username = 'root'
    password = 'AkueMax@2022'

    print("Connexion au serveur SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=30)

    py_script = """import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from logersn.views import property_detail_view

try:
    rf = RequestFactory()
    req = rf.get('/annonces/8b05818e-28eb-4793-b9e7-3a72c42ae7e4/', HTTP_HOST='logertogo.com')
    req.user = AnonymousUser()  # Assigner l'utilisateur anonyme pour éviter l'erreur de middleware
    
    res = property_detail_view(req, property_id='8b05818e-28eb-4793-b9e7-3a72c42ae7e4')
    
    html = res.content.decode('utf-8')
    print("=== Meta Tags ===")
    for line in html.split('\\n'):
        if '<meta' in line or '<title' in line:
            print(line.strip())
except Exception as e:
    import traceback
    traceback.print_exc()
"""

    sftp = ssh.open_sftp()
    remote_tmp = "/tmp/fetch_og.py"
    with sftp.file(remote_tmp, "w") as f:
        f.write(py_script)
    sftp.close()

    print("Injection...")
    ssh.exec_command(f"docker cp {remote_tmp} app-web-1:/app/fetch_og.py")

    print("Récupération des balises meta...")
    stdin, stdout, stderr = ssh.exec_command("docker compose -f /app/docker-compose.yml exec -T web python /app/fetch_og.py")
    
    print("STDOUT:")
    print(stdout.read().decode('utf-8', errors='replace').strip())
    print("STDERR:")
    print(stderr.read().decode('utf-8', errors='replace').strip())
    
    # Nettoyage
    ssh.exec_command(f"rm -f {remote_tmp}")
    ssh.exec_command("docker compose -f /app/docker-compose.yml exec -T web rm -f /app/fetch_og.py")
    
    ssh.close()

if __name__ == "__main__":
    main()
