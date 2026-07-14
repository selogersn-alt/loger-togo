import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def fix_and_rebuild():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        print("Connected.")
        
        print("Fixing Windows line endings (CRLF -> LF) on the server...")
        # Fix the file on the host
        ssh.exec_command("sed -i 's/\r$//' /app/scripts/entrypoint.sh")
        
        # Also ensure workers are set to 3
        ssh.exec_command("sed -i 's/workers 9/workers 3/g' /app/scripts/entrypoint.sh")
        ssh.exec_command("sed -i 's/Workers: 9/Workers: 3/g' /app/scripts/entrypoint.sh")
        
        print("Rebuilding Docker container with fixed file...")
        stdin, stdout, stderr = ssh.exec_command('cd /app && docker compose up -d --build web')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("\nSite successfully recovered and rebuilt!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_and_rebuild()
