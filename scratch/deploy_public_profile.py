import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Connexion au serveur {host}...")
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
sftp = ssh.open_sftp()

print("Déploiement de la carte interactive sur le profil public (logertogo.com)...")

local_path = r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\public_profile.html"
remote_path = "/app/templates/public_profile.html"

print(f"Upload de {remote_path}...")
sftp.put(local_path, remote_path)

sftp.close()

print("La mise à jour de la page publique a été effectuée !")
ssh.close()
