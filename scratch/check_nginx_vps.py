import paramiko
import sys

def check_nginx():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password, timeout=10)
    
    print("--- NGINX STATUS ---")
    stdin, stdout, stderr = ssh.exec_command("docker ps -a | grep nginx", get_pty=True)
    for line in stdout: sys.stdout.write(line)
    
    print("\n--- NGINX LOGS ---")
    stdin, stdout, stderr = ssh.exec_command("docker compose -f /app/docker-compose.yml logs --tail=50 nginx", get_pty=True)
    for line in stdout: sys.stdout.write(line)
    
    ssh.close()

if __name__ == "__main__":
    check_nginx()
