import paramiko
import os

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'
LOCAL_BASE = r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO"
REMOTE_BASE = "/app"

FILES_TO_DEPLOY = [
    "logertogo/views.py",
    "logertogo/urls.py",
    "templates/dashboard.html"
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
            
            # Ensure remote directory exists
            remote_dir = os.path.dirname(remote_file)
            ssh.exec_command(f"mkdir -p {remote_dir}")
            
            print(f"Uploading {file_path}...")
            sftp.put(local_file, remote_file)
        
        sftp.close()
        
        print("\nRestarting web container...")
        stdin, stdout, stderr = ssh.exec_command('cd /app && docker compose restart web')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("\nDéploiement terminé avec succès ! Le tableau de bord unifié est en ligne.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy()
