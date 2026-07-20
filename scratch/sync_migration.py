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

    remote_path = "/app/logersn/migrations/0036_property_visible_on_portal.py"
    local_path = "d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\logersn\\migrations\\0036_property_visible_on_portal.py"

    print(f"Téléchargement de {remote_path}...")
    sftp = ssh.open_sftp()
    try:
        sftp.get(remote_path, local_path)
        print(f"Fichier sauvegardé localement dans {local_path} !")
    except Exception as e:
        print(f"Erreur lors du téléchargement: {e}")
    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    main()
