import paramiko
import os
import time
import sys

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

files_to_deploy = [
    # Templates updated for sovereign branding
    (r"templates\management\pdf\rent_receipt.html", "/app/templates/management/pdf/rent_receipt.html"),
    (r"templates\management\pdf\lease_contract.html", "/app/templates/management/pdf/lease_contract.html"),
    (r"templates\lease_agreement_pdf.html", "/app/templates/lease_agreement_pdf.html"),
    (r"templates\hotel\hotel_booking_detail.html", "/app/templates/hotel/hotel_booking_detail.html"),
    (r"templates\agency\agency_receipt_pdf.html", "/app/templates/agency/agency_receipt_pdf.html"),
    # Python code for receptionist login
    (r"management\views_hotel.py", "/app/management/views_hotel.py"),
]

try:
    print(f"Connecting to {host}...")
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=60)
    print("Connected successfully!")

    sftp = ssh.open_sftp()
    
    print("\n1. Uploading updated sovereign templates to VPS...")
    for local_rel, remote_path in files_to_deploy:
        # Resolve absolute local path
        local_path = os.path.join(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO", local_rel)
        print(f"  Uploading {local_rel} -> {remote_path}...")
        
        # Ensure remote directory exists
        remote_dir = os.path.dirname(remote_path)
        try:
            sftp.stat(remote_dir)
        except IOError:
            # Try creating it
            ssh.exec_command(f"mkdir -p {remote_dir}")
            time.sleep(0.5)
            
        sftp.put(local_path, remote_path)
        
    sftp.close()
    print("All files successfully uploaded to VPS host!")

    print("\n2. Rebuilding the Docker container web service on VPS...")
    # This will bake the new templates into the container image
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
