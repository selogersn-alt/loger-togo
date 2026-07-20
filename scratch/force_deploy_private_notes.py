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

    files_to_deploy = [
        ("d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\logersn\\models.py", "/app/logersn/models.py"),
        ("d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\logersn\\migrations\\0036_property_private_contact_info.py", "/app/logersn/migrations/0036_property_private_contact_info.py"),
        ("d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\logersn\\forms.py", "/app/logersn/forms.py"),
        ("d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\templates\\property_form.html", "/app/templates/property_form.html"),
        ("d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\templates\\agency\\agency_property_form.html", "/app/templates/agency/agency_property_form.html"),
        ("d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\templates\\dashboard.html", "/app/templates/dashboard.html"),
        ("d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\templates\\agency\\agency_properties.html", "/app/templates/agency/agency_properties.html")
    ]

    print("Début du FORCE DEPLOY pour les notes privées...")

    sftp = ssh.open_sftp()
    for local_path, remote_path in files_to_deploy:
        print(f"Lecture locale: {local_path}")
        with open(local_path, "rb") as f:
            content = f.read()

        # S'assurer que le dossier parent existe sur l'hôte distant
        remote_dir = os.path.dirname(remote_path)
        try:
            sftp.stat(remote_dir)
        except IOError:
            print(f"Création du dossier distant {remote_dir}...")
            # Commande SSH pour créer le dossier récursivement
            ssh.exec_command(f"mkdir -p {remote_dir}")

        host_tmp = f"/tmp/{os.path.basename(remote_path)}"
        print(f"Upload vers l'hôte temporaire: {host_tmp}...")
        with sftp.file(host_tmp, 'wb') as f:
            f.write(content)

        print(f"Copie et injection dans le conteneur Docker pour: {remote_path}...")
        # Copie sur l'hôte
        cmd = f"mkdir -p {os.path.dirname(remote_path)} && cp {host_tmp} {remote_path} && cd /app && docker compose cp {host_tmp} web:{remote_path}"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.read()  # Attendre la fin

        # Copie alternative avec docker exec tee au cas où
        cmd_tee = f"cd /app && cat {host_tmp} | docker compose exec -T web tee {remote_path} > /dev/null"
        ssh.exec_command(cmd_tee)[1].read()
        
        # Nettoyage fichier temporaire
        try:
            sftp.remove(host_tmp)
        except Exception:
            pass

    sftp.close()

    print("Application des migrations Django en production...")
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web python manage.py migrate --noinput")
    print("STDOUT:")
    print(stdout.read().decode())
    print("STDERR:")
    print(stderr.read().decode())

    print("Redémarrage du conteneur web Docker...")
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart web")
    print(stdout.read().decode())

    ssh.close()
    print("FORCE DEPLOY PRIVÉ TERMINE AVEC SUCCÈS !")

if __name__ == "__main__":
    main()
