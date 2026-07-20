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

from logersn.models import Property

print("=== DEBUT INSPECTION VIEUX BIENS ===")
# Trier par date croissante pour avoir les plus anciens
for p in Property.objects.order_by('created_at')[:5]:
    print('ID:', str(p.id))
    print('Title:', p.title)
    print('Main Image URL:', p.get_main_image)
    print('Images Count:', p.images.count())
    for img in p.images.all():
        url = img.image_url.url if img.image_url else 'None'
        print('  - Name:', img.image_url.name, 'URL:', url)
    print('-' * 40)
print("=== FIN INSPECTION VIEUX BIENS ===")
"""

    sftp = ssh.open_sftp()
    remote_tmp = "/tmp/inspect_old.py"
    with sftp.file(remote_tmp, "w") as f:
        f.write(py_script)
    sftp.close()

    print("Injection...")
    ssh.exec_command(f"docker cp {remote_tmp} app-web-1:/app/inspect_old.py")

    print("Exécution de l'inspection...")
    stdin, stdout, stderr = ssh.exec_command("docker compose -f /app/docker-compose.yml exec -T web python /app/inspect_old.py")
    
    print("STDOUT:")
    print(stdout.read().decode('utf-8', errors='replace').strip())
    
    # Nettoyage
    ssh.exec_command(f"rm -f {remote_tmp}")
    ssh.exec_command("docker compose -f /app/docker-compose.yml exec -T web rm -f /app/inspect_old.py")
    
    ssh.close()

if __name__ == "__main__":
    main()
