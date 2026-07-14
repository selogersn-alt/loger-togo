import paramiko
import os

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'
REMOTE_DIR = '/app'

files_to_deploy = [
    (r"templates\base.html", "/app/templates/base.html"),
    (r"templates\hotel\base_hotel.html", "/app/templates/hotel/base_hotel.html"),
    (r"templates\agency\base_agency.html", "/app/templates/agency/base_agency.html"),
    (r"templates\hotel\hotel_booking_detail.html", "/app/templates/hotel/hotel_booking_detail.html"),
    (r"templates\agency\agency_receipt.html", "/app/templates/agency/agency_receipt.html"),
    (r"templates\hotel\print_invoice_hotel.html", "/app/templates/hotel/print_invoice_hotel.html"),
    (r"management\views_hotel.py", "/app/management/views_hotel.py"),
    (r"logertogo\urls_hotel.py", "/app/logertogo/urls_hotel.py"),
]

def deploy():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=60)
        sftp = ssh.open_sftp()
        print("Connected successfully!\n")
        
        base_local = r"D:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO"
        
        for local_rel, remote_file in files_to_deploy:
            local_file = os.path.join(base_local, local_rel)
            
            print(f"Uploading {local_file} -> {remote_file}")
            
            # Ensure remote directory exists
            remote_dir_only = os.path.dirname(remote_file)
            ssh.exec_command(f"mkdir -p {remote_dir_only}")
            
            sftp.put(local_file, remote_file)
            print("✓ Success")
            
        print("\nRestarting Docker Web Container...")
        stdin, stdout, stderr = ssh.exec_command('cd /app && docker compose up -d --build web')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Deployment session 5 completed successfully!")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        if 'sftp' in locals(): sftp.close()
        ssh.close()

if __name__ == "__main__":
    deploy()
