import paramiko
import sys

def restart_server():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("Connecting to VPS...")
    ssh.connect(hostname, username=username, password=password, timeout=10)
    
    try:
        print("Restarting web container...")
        stdin, stdout, stderr = ssh.exec_command('cd /app && docker compose restart web')
        print(stdout.read().decode('utf-8'))
        print(stderr.read().decode('utf-8'))
        print("Done!")
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    restart_server()
