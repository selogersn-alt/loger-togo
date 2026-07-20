import paramiko
import os

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
sftp = ssh.open_sftp()

print("1. Uploading patched logersn/views.py...")
sftp.put(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\logersn\views.py", "/app/logersn/views.py")

print("2. Uploading patched logertogo/views.py...")
sftp.put(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\logertogo\views.py", "/app/logertogo/views.py")

print("3. Uploading patched logertogo/urls.py...")
sftp.put(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\logertogo\urls.py", "/app/logertogo/urls.py")

print("4. Uploading new property_confirmation.html...")
sftp.put(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\property_confirmation.html", "/app/templates/property_confirmation.html")

sftp.close()

print("5. Restarting Gunicorn container...")
stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart web")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
print("SUBMISSION HOTFIX DEPLOYED SUCCESSFULLY!")
