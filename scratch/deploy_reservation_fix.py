import paramiko
import os

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Connexion au serveur {host}...")
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
sftp = ssh.open_sftp()

print("Mise à jour de logersn/views.py avec le pont de réservation...")
local_path = r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\logersn\views.py"
remote_path = "/app/logersn/views.py"
sftp.put(local_path, remote_path)
sftp.close()

print("Redémarrage du serveur web...")
ssh.exec_command("cd /app && docker compose restart web")

ssh.close()
print("RÉPARATION TERMINÉE ! Les réservations du portail arrivent désormais directement dans le SaaS de l'hôtel.")
