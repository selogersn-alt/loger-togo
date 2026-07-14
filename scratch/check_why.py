import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def check():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        
        # Get logs
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose logs web --tail=50")
        print("\n--- DOCKER COMPOSE LOGS WEB ---")
        logs = stdout.read().decode('utf-8', 'replace')
        print(logs)
        
        # Check if file has \r
        stdin, stdout, stderr = ssh.exec_command("cat -v /app/scripts/entrypoint.sh | head -n 5")
        print("\n--- ENTRYPOINT.SH HEADER ---")
        print(stdout.read().decode('utf-8', 'replace'))
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check()
