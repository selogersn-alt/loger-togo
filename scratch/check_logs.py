import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def check_logs():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        
        print("Checking container status...")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose ps")
        print(stdout.read().decode('utf-8', 'replace'))
        
        print("Checking web container logs...")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose logs web --tail=50")
        print(stdout.read().decode('utf-8', 'replace'))
        print(stderr.read().decode('utf-8', 'replace'))
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_logs()
