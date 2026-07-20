import paramiko

def fetch_logs():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password, timeout=10)
    
    stdin, stdout, stderr = ssh.exec_command('docker compose -f /app/docker-compose.yml logs --tail=20 nginx')
    print("=== LAST 20 NGINX LOGS ===")
    print(stdout.read().decode('utf-8'))
    
    # Also fetch the web container logs just in case there are python errors
    stdin, stdout, stderr = ssh.exec_command('docker compose -f /app/docker-compose.yml logs --tail=20 web')
    print("=== LAST 20 WEB LOGS ===")
    print(stdout.read().decode('utf-8'))

    ssh.close()

if __name__ == "__main__":
    fetch_logs()
