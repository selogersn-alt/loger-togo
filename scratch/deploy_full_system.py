import paramiko
import os
import time
import sys

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

files_to_deploy = [
    # 1. Database models & migration
    (r"management\models.py", "/app/management/models.py"),
    (r"management\migrations\0015_employee_management.py", "/app/management/migrations/0015_employee_management.py"),
    (r"management\migrations\0016_attendance_geolocation.py", "/app/management/migrations/0016_attendance_geolocation.py"),
    (r"management\migrations\0017_employee_action_logs.py", "/app/management/migrations/0017_employee_action_logs.py"),
    
    # 2. Views, Routing & Emails (Hôtel & Agence)
    (r"logertogo\emails.py", "/app/logertogo/emails.py"),
    (r"management\views_hotel.py", "/app/management/views_hotel.py"),
    (r"management\views_agency.py", "/app/management/views_agency.py"),
    (r"logertogo\urls_hotel.py", "/app/logertogo/urls_hotel.py"),
    (r"logertogo\urls_agence.py", "/app/logertogo/urls_agence.py"),
    
    # 3. Upgraded HTML templates (Hôtel & Agence)
    (r"templates\hotel\base_hotel.html", "/app/templates/hotel/base_hotel.html"),
    (r"templates\hotel\hotel_rooms.html", "/app/templates/hotel/hotel_rooms.html"),
    (r"templates\hotel\hotel_dashboard.html", "/app/templates/hotel/hotel_dashboard.html"),
    (r"templates\hotel\hotel_sub_agents.html", "/app/templates/hotel/hotel_sub_agents.html"),
    
    (r"templates\agency\base_agency.html", "/app/templates/agency/base_agency.html"),
    (r"templates\agency\agency_dashboard.html", "/app/templates/agency/agency_dashboard.html"),
    (r"templates\agency\agency_sub_agents.html", "/app/templates/agency/agency_sub_agents.html"),
]

try:
    print(f"Connecting to {host}...")
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=60)
    print("Connected successfully!")

    sftp = ssh.open_sftp()
    
    print("\n1. Uploading all Employee Management system files to VPS...")
    for local_rel, remote_path in files_to_deploy:
        local_path = os.path.join(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO", local_rel)
        print(f"  Uploading {local_rel} -> {remote_path}...")
        
        remote_dir = os.path.dirname(remote_path)
        try:
            sftp.stat(remote_dir)
        except IOError:
            ssh.exec_command(f"mkdir -p {remote_dir}")
            time.sleep(0.5)
            
        sftp.put(local_path, remote_path)
        
    sftp.close()
    print("All files successfully uploaded to VPS host!")

    print("\n2. Rebuilding the Docker container web service on VPS...")
    # This will bake the new models, migration, views, routes and templates into the container image
    # The entrypoint will automatically apply migration 0015!
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose up -d --build web")
    
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            print(stdout.channel.recv(1024).decode('utf-8', 'replace'), end='')
        if stderr.channel.recv_stderr_ready():
            print(stderr.channel.recv_stderr(1024).decode('utf-8', 'replace'), end='', file=sys.stderr)
        time.sleep(0.5)

    print(stdout.read().decode('utf-8', 'replace'))
    print(stderr.read().decode('utf-8', 'replace'))

    print("\n3. Waiting 5 seconds and checking web service logs...")
    time.sleep(5)
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose logs web --tail=50")
    print(stdout.read().decode('utf-8', 'replace'))

except Exception as e:
    print(f"Error during deployment: {e}")
finally:
    ssh.close()
    print("\nFINISHED!")
