import paramiko

def check_server():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password, timeout=10)
    
    stdin, stdout, stderr = ssh.exec_command('cat /app/logertogo/urls.py | grep "paiement"')
    print("=== SERVER URLS.PY ===")
    print(stdout.read().decode('utf-8'))
    
    ssh.close()

if __name__ == "__main__":
    check_server()
