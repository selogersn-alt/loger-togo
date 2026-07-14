import paramiko
import os

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def deploy_workers():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=60)
        sftp = ssh.open_sftp()
        print("Connected successfully!\n")
        
        base_local = r"D:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO"
        local_file = os.path.join(base_local, r"scripts\entrypoint.sh")
        remote_file = "/app/scripts/entrypoint.sh"
        
        print(f"Uploading {local_file} -> {remote_file}")
        
        # Ensure remote directory exists
        ssh.exec_command("mkdir -p /app/scripts")
        sftp.put(local_file, remote_file)
        
        # Make it executable
        ssh.exec_command("chmod +x /app/scripts/entrypoint.sh")
        print("✓ Fichier entrypoint.sh envoyé avec succès")
        
        print("\nRedémarrage du conteneur Web pour appliquer les 9 workers...")
        stdin, stdout, stderr = ssh.exec_command('cd /app && docker compose up -d --build web')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Mise à jour des workers terminée avec succès !")
        
    except Exception as e:
        print(f"Erreur lors du déploiement: {e}")
    finally:
        if 'sftp' in locals(): sftp.close()
        ssh.close()

if __name__ == "__main__":
    deploy_workers()
