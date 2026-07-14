import paramiko
import os
import time
import subprocess

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'
LOCAL_BASE = r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO"
REMOTE_BASE = "/app"

def fix_and_deploy():
    req_path = os.path.join(LOCAL_BASE, "requirements.txt")
    print("1. Restoring original requirements.txt from Git...")
    
    # Run git checkout locally to restore the file
    subprocess.run(["git", "checkout", "requirements.txt"], cwd=LOCAL_BASE)
    
    print("2. Ensuring django-ckeditor and Pillow are present...")
    # Read the restored file
    # We must handle potential UTF-16LE or UTF-8
    try:
        with open(req_path, 'rb') as f:
            raw = f.read()
        if raw.startswith(b'\xff\xfe'):
            content = raw.decode('utf-16le')
        else:
            content = raw.decode('utf-8')
    except Exception as e:
        print("Fallback decode:", e)
        content = raw.decode('utf-8', errors='ignore')
        
    lines = content.splitlines()
    clean_lines = [l.strip() for l in lines if l.strip()]
    
    # Check if ckeditor is there
    if not any('django-ckeditor' in l for l in clean_lines):
        clean_lines.append('django-ckeditor')
    if not any('Pillow' in l for l in clean_lines):
        clean_lines.append('Pillow')
        
    # Write it back as pure UTF-8
    with open(req_path, 'w', encoding='utf-8') as f:
        for line in clean_lines:
            f.write(line + '\n')
            
    print("requirements.txt has been fully repaired (UTF-8, intact).")
    
    print("\n3. Connecting to server for deployment...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        sftp = ssh.open_sftp()
        
        print(f"Uploading requirements.txt to {REMOTE_BASE}/requirements.txt...")
        sftp.put(req_path, f"{REMOTE_BASE}/requirements.txt")
        sftp.close()
        
        print("\n4. Rebuilding the Docker container web service...")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose up -d --build web")
        
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode('utf-8', 'replace'), end='')
            time.sleep(0.5)
            
        print(stdout.read().decode('utf-8', 'replace'))
        print(stderr.read().decode('utf-8', 'replace'))
        
        print("\n5. Clearing Django cache...")
        cmd_cache = 'cd /app && docker compose exec -T web python manage.py shell -c "from django.core.cache import cache; cache.clear()"'
        ssh.exec_command(cmd_cache)
        
        print("\nOpération terminée et le serveur est de nouveau en ligne !")
        
    except Exception as e:
        print(f"Deployment Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_and_deploy()
