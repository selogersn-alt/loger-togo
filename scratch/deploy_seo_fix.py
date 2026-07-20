import paramiko
import os

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
sftp = ssh.open_sftp()

print("1. Uploading patched property_detail.html...")
sftp.put(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\property_detail.html", "/app/templates/property_detail.html")

print("2. Uploading patched base.html...")
sftp.put(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\base.html", "/app/templates/base.html")

sftp.close()

print("3. Restarting Gunicorn container...")
stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart web")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
print("SEO HOTFIX DEPLOYED SUCCESSFULLY!")
