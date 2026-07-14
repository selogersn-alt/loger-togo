import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Connexion au serveur {host}...")
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
sftp = ssh.open_sftp()

print("Déploiement de la carte interactive sur le profil Agence...")

files_to_upload = [
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\management\views_agency.py", "/app/management/views_agency.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\agency\agency_profile.html", "/app/templates/agency/agency_profile.html")
]

for local_path, remote_path in files_to_upload:
    print(f"Upload de {remote_path}...")
    sftp.put(local_path, remote_path)

sftp.close()

print("Redémarrage du serveur web...")
ssh.exec_command("cd /app && docker compose restart web")

ssh.close()
print("RÉPARATION TERMINÉE ! La carte est maintenant disponible sur agence.logertogo.com")
