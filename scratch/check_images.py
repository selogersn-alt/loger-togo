import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def check():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        
        # Check files inside the container's media directory
        print("Checking media directory inside container...")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web ls -la /app/media/blog/posts/2026/05")
        out = stdout.read().decode()
        err = stderr.read().decode()
        print("STDOUT:", out)
        print("STDERR:", err)
        
        # Check host directory
        print("Checking media directory on host...")
        stdin, stdout, stderr = ssh.exec_command("ls -la /app/media/blog/posts/2026/05")
        out = stdout.read().decode()
        err = stderr.read().decode()
        print("STDOUT:", out)
        print("STDERR:", err)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check()
