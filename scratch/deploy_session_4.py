import paramiko
import os
import time
import sys

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

files_to_deploy = [
    # Models
    (r"logersn\models.py", "/app/logersn/models.py"),
    (r"management\models.py", "/app/management/models.py"),
    
    # Views & APIs
    (r"logersn\views.py", "/app/logersn/views.py"),
    (r"management\views_hotel.py", "/app/management/views_hotel.py"),
    (r"management\views_agency.py", "/app/management/views_agency.py"),
    (r"management\views_notifications.py", "/app/management/views_notifications.py"),
    
    # URLs
    (r"logertogo\urls_hotel.py", "/app/logertogo/urls_hotel.py"),
    (r"logertogo\urls_agence.py", "/app/logertogo/urls_agence.py"),
    
    # Templates
    (r"templates\logersn\near_me.html", "/app/templates/logersn/near_me.html"),
    (r"templates\hotel\hotel_room_form.html", "/app/templates/hotel/hotel_room_form.html"),
    (r"templates\agency\agency_property_form.html", "/app/templates/agency/agency_property_form.html"),
    (r"templates\hotel\base_hotel.html", "/app/templates/hotel/base_hotel.html"),
    (r"templates\agency\base_agency.html", "/app/templates/agency/base_agency.html"),
    (r"templates\hotel\hotel_dashboard.html", "/app/templates/hotel/hotel_dashboard.html"),
    (r"templates\agency\agency_dashboard.html", "/app/templates/agency/agency_dashboard.html"),
    (r"templates\hotel\hotel_sub_agents.html", "/app/templates/hotel/hotel_sub_agents.html"),
    (r"templates\agency\agency_sub_agents.html", "/app/templates/agency/agency_sub_agents.html"),
]

try:
    print(f"Connecting to {host}...")
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=60)
    print("Connected successfully!")

    sftp = ssh.open_sftp()
    
    print("\n1. Uploading modified files to VPS...")
    for local_rel, remote_path in files_to_deploy:
        local_path = os.path.join(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO", local_rel)
        if os.path.exists(local_path):
            print(f"  Uploading {local_rel} -> {remote_path}...")
            remote_dir = os.path.dirname(remote_path)
            try:
                sftp.stat(remote_dir)
            except IOError:
                ssh.exec_command(f"mkdir -p {remote_dir}")
                time.sleep(0.5)
            sftp.put(local_path, remote_path)
        else:
            print(f"  Skipping {local_rel} (file not found locally).")
        
    sftp.close()
    print("All files successfully uploaded to VPS host!")

    print("\n2. Rebuilding and starting the web service container...")
    # We must build first so the newly uploaded files (which fix the ImportError) are baked into the image
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose up -d --build web")
    print(stdout.read().decode('utf-8', 'replace'))
    print(stderr.read().decode('utf-8', 'replace'))
    
    print("\n3. Waiting 5 seconds for the container to stabilize...")
    time.sleep(5)

    print("\n4. Running database migrations on the VPS directly...")
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web python manage.py makemigrations")
    print(stdout.read().decode('utf-8', 'replace'))
    print(stderr.read().decode('utf-8', 'replace'))
    
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web python manage.py migrate")
    print(stdout.read().decode('utf-8', 'replace'))
    print(stderr.read().decode('utf-8', 'replace'))

except Exception as e:
    print(f"Error during deployment: {e}")
finally:
    ssh.close()
    print("\nFINISHED!")
