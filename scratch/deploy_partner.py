import paramiko
import os
import time

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'
LOCAL_BASE = r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO"
REMOTE_BASE = "/app"

TEMPLATES = [
    "templates/base.html",
    "templates/register.html",
    "templates/management/create_lease.html",
    "templates/hotel/hotel_promo.html",
    "templates/emails/base_email.html"
]

def deploy_and_rebuild():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to server...")
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        
        sftp = ssh.open_sftp()
        print("Uploading updated templates (with Loger Benin and fixed phone)...")
        for tpl in TEMPLATES:
            local_path = os.path.join(LOCAL_BASE, tpl).replace('/', '\\')
            remote_path = f"{REMOTE_BASE}/{tpl}"
            print(f"Uploading {tpl} to {remote_path}...")
            sftp.put(local_path, remote_path)
        sftp.close()
        
        print("\nRebuilding the Docker container web service to apply template changes...")
        # We need to build because templates are copied into the Docker image, not mounted
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose up -d --build web")
        
        # Stream the output
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode('utf-8', 'replace'), end='')
            time.sleep(0.5)
            
        print(stdout.read().decode('utf-8', 'replace'))
        print(stderr.read().decode('utf-8', 'replace'))
        
        print("\nClearing Django cache for safety...")
        cmd_cache = 'cd /app && docker compose exec -T web python manage.py shell -c "from django.core.cache import cache; cache.clear()"'
        ssh.exec_command(cmd_cache)
        
        print("Opération terminée !")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_and_rebuild()
