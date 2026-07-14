import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def fix_perms():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        
        print("Fixing permissions as root inside the container...")
        commands = [
            "cd /app && docker compose exec -u root -T web chown -R 999:999 /app/media/blog",
            "cd /app && docker compose exec -u root -T web chmod -R 755 /app/media/blog"
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read() # block until finished
            err = stderr.read().decode('utf-8', 'replace')
            if err:
                print(f"Warning/Error on '{cmd}': {err}")
                
        print("Permissions corrigées avec succès !")
        
    except Exception as e:
        print(f"Connection Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_perms()
