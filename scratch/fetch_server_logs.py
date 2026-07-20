import paramiko

def main():
    host = "157.180.127.70"
    username = 'root'
    password = 'AkueMax@2022'

    print("Connexion au serveur SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=30)

    print("=== Production Django Container Logs (web) ===")
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose logs --tail=100 web")
    print("STDOUT:")
    print(stdout.read().decode('utf-8', errors='replace'))
    print("STDERR:")
    print(stderr.read().decode('utf-8', errors='replace'))
    
    ssh.close()

if __name__ == "__main__":
    main()
