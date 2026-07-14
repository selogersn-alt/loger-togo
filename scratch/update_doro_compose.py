import paramiko

VPS_HOST = '157.180.127.70'
VPS_USER = 'root'
VPS_PASS = 'AkueMax@2022'
REMOTE_FILE = '/var/www/DOROCAVIAR/docker-compose.yml'
LOCAL_FILE = 'D:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\DOROCAVIAR\\docker-compose.yml'

def main():
    print("=" * 60)
    print("  UPLOADING UPDATED DOCKER-COMPOSE FOR DOROCAVIAR")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {VPS_HOST}...")
        ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=15)
        print("[OK] Connected successfully!")
        
        # Open SFTP
        print("Uploading docker-compose.yml...")
        sftp = ssh.open_sftp()
        sftp.put(LOCAL_FILE, REMOTE_FILE)
        sftp.close()
        print("[OK] Uploaded successfully!")
        
        # Apply the new docker-compose file (restarts the containers with the new policy)
        cmd = "cd /var/www/DOROCAVIAR && docker compose up -d"
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))
        print("[OK] Restart policies successfully updated on the VPS!")
        
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
