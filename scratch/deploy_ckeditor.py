import paramiko
import os

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'
LOCAL_BASE = r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO"
REMOTE_BASE = "/app"

FILES_TO_DEPLOY = [
    "logertogo/settings.py",
    "logertogo/urls.py",
    "blog/models.py",
]

def deploy():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        sftp = ssh.open_sftp()
        
        for file_path in FILES_TO_DEPLOY:
            local_file = os.path.join(LOCAL_BASE, file_path).replace('/', '\\')
            remote_file = f"{REMOTE_BASE}/{file_path}"
            print(f"Uploading {file_path}...")
            sftp.put(local_file, remote_file)
            
        sftp.close()
        
        print("\nInstalling django-ckeditor in the container and running migrations...")
        
        commands = [
            "echo '\ndjango-ckeditor' >> /app/requirements.txt",
            "cd /app && docker compose exec -T web pip install django-ckeditor",
            "cd /app && docker compose exec -T web python manage.py makemigrations blog",
            "cd /app && docker compose exec -T web python manage.py migrate",
            "cd /app && docker compose exec -T web python manage.py collectstatic --noinput",
            "cd /app && docker compose restart web"
        ]
        
        for cmd in commands:
            print(f"Running: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            out = stdout.read().decode('utf-8', 'replace')
            err = stderr.read().decode('utf-8', 'replace')
            if out: print(out)
            if err: print(f"ERROR: {err}")
            
        print("\nDéploiement terminé ! L'éditeur de texte est installé.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
