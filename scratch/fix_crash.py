import paramiko
import os

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def fix_crash():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        print("Connected.")
        
        # Get logs to see what crashed
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose logs web --tail=20")
        print("\n--- LOGS WEB ---")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # Revert entrypoint to 3 workers directly on server
        ssh.exec_command("sed -i 's/workers 9/workers 3/g' /app/scripts/entrypoint.sh")
        ssh.exec_command("sed -i 's/Workers: 9/Workers: 3/g' /app/scripts/entrypoint.sh")
        
        # Fix line endings just in case (dos2unix equivalent)
        ssh.exec_command("sed -i 's/\r$//' /app/scripts/entrypoint.sh")
        
        # Restart web
        print("\nRestarting web container...")
        stdin, stdout, stderr = ssh.exec_command('cd /app && docker compose restart web')
        print(stdout.read().decode())
        
        print("\nFix applied successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_crash()
