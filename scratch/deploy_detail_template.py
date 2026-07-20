import paramiko

def main():
    host = "157.180.127.70"
    username = 'root'
    password = 'AkueMax@2022'

    print("Connexion au serveur SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=30)

    local_path = "d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\templates\\property_detail.html"
    remote_tmp = "/tmp/property_detail.html"
    remote_host_path = "/app/templates/property_detail.html"
    container_path = "/app/templates/property_detail.html"

    print("Uploading property_detail.html to host...")
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_tmp)
    sftp.close()

    print("Copying to host templates folder...")
    ssh.exec_command(f"cp {remote_tmp} {remote_host_path}")

    print("Copying into Docker container...")
    ssh.exec_command(f"docker cp {remote_tmp} app-web-1:{container_path}")

    # Nettoyer /tmp
    ssh.exec_command(f"rm -f {remote_tmp}")
    
    # Redémarrer gunicorn/web pour vider le cache des templates
    print("Redémarrage du conteneur web pour vider le cache des templates...")
    ssh.exec_command("cd /app && docker compose restart web")

    ssh.close()
    print("Mise à jour du template de détail terminée !")

if __name__ == "__main__":
    main()
