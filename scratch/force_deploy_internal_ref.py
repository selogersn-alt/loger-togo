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

    # local and remote paths for migration 0038
    local_path = "d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\logersn\\migrations\\0038_property_internal_ref.py"
    remote_tmp = "/tmp/0038_property_internal_ref.py"
    remote_host_path = "/app/logersn/migrations/0038_property_internal_ref.py"
    container_path = "/app/logersn/migrations/0038_property_internal_ref.py"

    print("Uploading 0038 migration to host...")
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_tmp)
    sftp.close()

    print("Copying to host migrations folder...")
    ssh.exec_command(f"cp {remote_tmp} {remote_host_path}")

    print("Copying 0038 migration into Docker container web...")
    ssh.exec_command(f"docker cp {remote_tmp} app-web-1:{container_path}")

    # Nettoyer /tmp
    ssh.exec_command(f"rm -f {remote_tmp}")

    print("Application de la migration 0038 en production...")
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web python manage.py migrate --noinput")
    print("STDOUT:")
    print(stdout.read().decode())
    print("STDERR:")
    print(stderr.read().decode())

    print("Redémarrage du conteneur Docker web...")
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart web")
    print(stdout.read().decode())

    ssh.close()
    print("Déploiement et application de la migration 0038 terminés avec succès !")

if __name__ == "__main__":
    main()
