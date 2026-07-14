import paramiko
import os

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'
REMOTE_DIR = '/app'

files_to_deploy = [
    (r"chat\views.py", "/app/chat/views.py"),
    (r"management\views_agency.py", "/app/management/views_agency.py"),
    (r"templates\agency\base_agency.html", "/app/templates/agency/base_agency.html"),
    (r"logertogo\urls_agence.py", "/app/logertogo/urls_agence.py"),
    (r"templates\chat\messagerie.html", "/app/templates/chat/messagerie.html"),
    (r"templates\agency\agency_applications.html", "/app/templates/agency/agency_applications.html"),
    (r"management\models.py", "/app/management/models.py"),
    (r"logersn\views.py", "/app/logersn/views.py"),
    (r"templates\hotel\hotel_bookings.html", "/app/templates/hotel/hotel_bookings.html"),
    (r"templates\hotel\hotel_booking_detail.html", "/app/templates/hotel/hotel_booking_detail.html"),
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
            
        print("\nUploading migrations...")
        migration_dir = os.path.join(base_local, r"management\migrations")
        for filename in os.listdir(migration_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                local_file = os.path.join(migration_dir, filename)
                remote_file = f"/app/management/migrations/{filename}"
                try:
                    sftp.put(local_file, remote_file)
                except Exception:
                    pass
        print("✓ Migrations uploaded")

        print("\nApplying Migrations on Server...")
        stdin, stdout, stderr = ssh.exec_command('cd /app && docker compose exec web python manage.py migrate management')
        print(stdout.read().decode())
        print(stderr.read().decode())

        print("\nRestarting Docker Web Container...")
        stdin, stdout, stderr = ssh.exec_command('cd /app && docker compose restart web')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Deployment session 6 completed successfully!")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        if 'sftp' in locals(): sftp.close()
        ssh.close()

if __name__ == "__main__":
    deploy()
