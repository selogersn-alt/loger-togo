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

    # 1. Supprimer le fichier temporaire provoquant le crash en production
    print("1. Suppression du fichier en conflit en production...")
    stdin, stdout, stderr = ssh.exec_command("rm -f /app/logersn/migrations/0036_property_private_contact_info.py")
    stdout.read()

    # 2. Télécharger le fichier existant en production localement
    remote_path = "/app/logersn/migrations/0036_property_visible_on_portal.py"
    local_path = "d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\logersn\\migrations\\0036_property_visible_on_portal.py"
    
    print(f"2. Téléchargement de {remote_path} vers {local_path}...")
    sftp = ssh.open_sftp()
    try:
        sftp.get(remote_path, local_path)
        print(f"-> Fichier récupéré et sauvegardé localement !")
    except Exception as e:
        print(f"-> Impossible de télécharger (le fichier n'existe peut-être pas encore sur l'hôte): {e}")
    finally:
        sftp.close()

    # 3. Redémarrer le conteneur web pour relancer le site
    print("3. Redémarrage du serveur web Docker en production...")
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart web")
    print(stdout.read().decode())
    
    ssh.close()
    print("Opération terminée. Le site devrait être de retour en ligne !")

if __name__ == "__main__":
    main()
