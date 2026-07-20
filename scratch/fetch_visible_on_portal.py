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

    # Copier le fichier depuis le conteneur arrêté/crashé vers le répertoire /tmp de l'hôte
    print("Tentative de copie du fichier depuis le conteneur Docker vers l'hôte...")
    
    # On essaie d'abord avec docker compose cp, puis avec docker cp sur le conteneur app-web-1
    commands = [
        "cd /app && docker compose cp web:/app/logersn/migrations/0036_property_visible_on_portal.py /tmp/visible_on_portal.py",
        "docker cp app-web-1:/app/logersn/migrations/0036_property_visible_on_portal.py /tmp/visible_on_portal.py"
    ]
    
    success = False
    for cmd in commands:
        print(f"Exécution: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        err = stderr.read().decode().strip()
        out = stdout.read().decode().strip()
        if err:
            print(f"Erreur/Warning: {err}")
        else:
            print("Copie réussie !")
            success = True
            break

    if success:
        # Télécharger le fichier récupéré
        remote_path = "/tmp/visible_on_portal.py"
        local_path = "d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\logersn\\migrations\\0036_property_visible_on_portal.py"
        
        print(f"Téléchargement du fichier temporaire depuis {remote_path}...")
        sftp = ssh.open_sftp()
        try:
            sftp.get(remote_path, local_path)
            print(f"Succès ! Fichier enregistré localement sous: {local_path}")
            
            # Nettoyer /tmp
            sftp.remove(remote_path)
        except Exception as e:
            print(f"Erreur de téléchargement SFTP: {e}")
        finally:
            sftp.close()
    else:
        print("Échec des tentatives de copie. Le fichier n'existe peut-être pas ou le conteneur a été supprimé.")

    ssh.close()

if __name__ == "__main__":
    main()
