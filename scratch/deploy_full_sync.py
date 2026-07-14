import paramiko
import os

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Connecting to {host}...")
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
sftp = ssh.open_sftp()

files_to_upload = [
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\management\models.py", "/app/management/models.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\management\views_hotel.py", "/app/management/views_hotel.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\users\models.py", "/app/users/models.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\logersn\views.py", "/app/logersn/views.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\hotel\hotel_profile.html", "/app/templates/hotel/hotel_profile.html"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\logersn\near_me.html", "/app/templates/logersn/near_me.html"),
]

for local_path, remote_path in files_to_upload:
    print(f"Uploading {os.path.basename(local_path)}...")
    sftp.put(local_path, remote_path)

sftp.close()

print("Applying migrations on the server...")
stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web python manage.py makemigrations users management logersn")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web python manage.py migrate")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

print("Restarting Gunicorn container...")
stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart web")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
print("FULL SYNC DEPLOYED SUCCESSFULLY!")
