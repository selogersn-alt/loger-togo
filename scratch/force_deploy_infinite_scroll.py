import paramiko
import os

def main():
    host = "157.180.127.70"
    username = 'root'
    password = 'AkueMax@2022'

    print("Connexion au serveur SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=30)

    # local path structures
    files_to_deploy = [
        {
            "local": "d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\logersn\\views.py",
            "remote": "/app/logersn/views.py"
        },
        {
            "local": "d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\templates\\partials\\property_grid_items.html",
            "remote": "/app/templates/partials/property_grid_items.html"
        },
        {
            "local": "d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\templates\\properties_list.html",
            "remote": "/app/templates/properties_list.html"
        }
    ]

    sftp = ssh.open_sftp()
    
    for f in files_to_deploy:
        filename = os.path.basename(f["local"])
        temp_remote = f"/tmp/{filename}"
        
        print(f"Uploading {filename} to /tmp...")
        sftp.put(f["local"], temp_remote)
        
        print(f"Copying to host path {f['remote']}...")
        # Create directories if they don't exist
        remote_dir = os.path.dirname(f["remote"])
        ssh.exec_command(f"mkdir -p {remote_dir}")
        ssh.exec_command(f"cp {temp_remote} {f['remote']}")
        
        print(f"Injecting into Docker container...")
        ssh.exec_command(f"docker cp {temp_remote} app-web-1:{f['remote']}")
        
        # Clean tmp
        ssh.exec_command(f"rm -f {temp_remote}")
        
    sftp.close()

    print("Redémarrage du conteneur Docker web pour appliquer les modifications...")
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart web")
    print(stdout.read().decode())

    ssh.close()
    print("Déploiement de l'Infinite Scroll terminé avec succès !")

if __name__ == "__main__":
    main()
