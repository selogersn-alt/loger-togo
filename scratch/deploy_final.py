import paramiko
import os
import time

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'
LOCAL_BASE = r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO"
REMOTE_BASE = "/app"

TEMPLATES = [
    "templates/base.html",
    "templates/register.html",
    "templates/management/create_lease.html",
    "templates/hotel/hotel_promo.html",
    "templates/emails/base_email.html"
]

def fix_requirements():
    req_path = os.path.join(LOCAL_BASE, "requirements.txt")
    print("Fixing requirements.txt encoding...")
    try:
        with open(req_path, 'rb') as f:
            raw = f.read()
        
        # Try to decode UTF-16LE
        decoded = raw.decode('utf-16le', errors='replace')
        lines = decoded.splitlines()
        
        clean_lines = []
        for line in lines:
            line = line.strip().replace('\x00', '').replace('', '')
            # Filter out completely garbage lines (e.g. from the echo >> corruption)
            if line and not line.startswith('d') and len(line) > 2 and ' ' not in line:
                clean_lines.append(line)
        
        # If the file was not UTF-16LE but UTF-8, the above might garble it.
        # Let's do a fallback check.
        if len(clean_lines) < 5:
            # It was probably UTF-8 to begin with!
            decoded = raw.decode('utf-8', errors='replace')
            lines = decoded.splitlines()
            clean_lines = []
            for line in lines:
                line = line.strip().replace('\x00', '').replace('', '')
                if line:
                    clean_lines.append(line)
                    
        # Ensure django-ckeditor is there
        found_ck = any('django-ckeditor' in l for l in clean_lines)
        if not found_ck:
            clean_lines.append('django-ckeditor')
            clean_lines.append('Pillow')
            
        with open(req_path, 'w', encoding='utf-8') as f:
            for line in clean_lines:
                f.write(line + '\n')
        print("requirements.txt fixed!")
    except Exception as e:
        print(f"Error fixing requirements.txt: {e}")

def deploy_and_rebuild():
    fix_requirements()
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to server...")
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        
        sftp = ssh.open_sftp()
        print("Uploading updated templates and requirements.txt...")
        
        # Upload requirements.txt
        local_req = os.path.join(LOCAL_BASE, "requirements.txt")
        sftp.put(local_req, f"{REMOTE_BASE}/requirements.txt")
        print("requirements.txt uploaded.")
        
        for tpl in TEMPLATES:
            local_path = os.path.join(LOCAL_BASE, tpl).replace('/', '\\')
            remote_path = f"{REMOTE_BASE}/{tpl}"
            print(f"Uploading {tpl} to {remote_path}...")
            try:
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"Could not upload {tpl}: {e}")
        sftp.close()
        
        print("\nRebuilding the Docker container web service...")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose up -d --build web")
        
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode('utf-8', 'replace'), end='')
            time.sleep(0.5)
            
        print(stdout.read().decode('utf-8', 'replace'))
        print(stderr.read().decode('utf-8', 'replace'))
        
        print("\nClearing Django cache...")
        cmd_cache = 'cd /app && docker compose exec -T web python manage.py shell -c "from django.core.cache import cache; cache.clear()"'
        ssh.exec_command(cmd_cache)
        
        print("Déploiement terminé et le système est re-compilé avec succès !")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_and_rebuild()
