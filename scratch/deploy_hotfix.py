import paramiko
import os

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
sftp = ssh.open_sftp()

print("1. Uploading patched models.py...")
sftp.put(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\management\models.py", "/app/management/models.py")

print("2. Uploading patched views_hotel.py...")
sftp.put(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\management\views_hotel.py", "/app/management/views_hotel.py")

print("3. Uploading new migration...")
sftp.put(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\management\migrations\0014_remove_hotelbooking_extra_charges.py", "/app/management/migrations/0014_remove_hotelbooking_extra_charges.py")
sftp.close()

print("4. Applying migration on the server...")
stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web python manage.py migrate --noinput")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

print("5. Restarting Gunicorn container...")
stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart web")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
print("HOTFIX DEPLOYED SUCCESSFULLY!")
