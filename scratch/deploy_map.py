import paramiko
import os
import time
import sys

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

files_to_deploy = [
    (r"templates\base.html", "/app/templates/base.html"),
    (r"templates\home.html", "/app/templates/home.html"),
    (r"templates\agency\agency_property_form.html", "/app/templates/agency/agency_property_form.html"),
    (r"templates\logersn\near_me.html", "/app/templates/logersn/near_me.html"),
    (r"logersn\views.py", "/app/logersn/views.py"),
]

try:
    print(f"Connecting to {host}...")
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=60)
    print("Connected successfully!")

    sftp = ssh.open_sftp()
    
    print("\n1. Uploading Map Search feature files to VPS...")
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
