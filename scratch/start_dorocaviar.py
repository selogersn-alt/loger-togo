import paramiko
import sys

VPS_HOST = '157.180.127.70'
VPS_USER = 'root'
VPS_PASS = 'AkueMax@2022'
DORO_PATH = '/var/www/DOROCAVIAR'

def main():
    print("=" * 60)
    print("        STARTING DOROCAVIAR ON HETZNER VPS")
    print("=" * 60)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {VPS_HOST}...")
        ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=15)
        print("[OK] Connected successfully!")
        
        # Start containers
        cmd = f"cd {DORO_PATH} && docker compose up -d"
        print(f"Executing command: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        
        if out:
            print("\n--- STDOUT ---")
            print(out)
        if err:
            print("\n--- STDERR ---")
            print(err)
            
        # Verify status
        print("\nVerifying containers status...")
        stdin, stdout, stderr = ssh.exec_command("docker ps -a --filter name=dorocaviar")
        print(stdout.read().decode('utf-8'))
        
    except Exception as e:
        print(f"[ERROR] Failed to start containers: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
