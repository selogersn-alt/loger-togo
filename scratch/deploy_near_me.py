import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Connexion au serveur {host}...")
try:
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
except Exception as e:
    print(f"Erreur de connexion SSH: {e}")
    exit(1)

sftp = ssh.open_sftp()

files_to_upload = [
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\logersn\views.py", "/app/logersn/views.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\logersn\near_me.html", "/app/templates/logersn/near_me.html")
]

print("=== DEPLOIEMENT DES FICHIERS ===")
for local_path, remote_path in files_to_upload:
    print(f"Upload de {remote_path}...")
    try:
        sftp.put(local_path, remote_path)
    except Exception as e:
        print(f"Erreur lors de l'upload de {local_path}: {e}")

sftp.close()

print("\n=== REDEMARRAGE DU SERVEUR WEB ===")
ssh.exec_command("cd /app && docker compose restart web")

ssh.close()
print("DEPLOIEMENT TERMINÉ ! La nouvelle carte est en ligne.")
