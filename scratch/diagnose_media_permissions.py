import paramiko

def main():
    host = "157.180.127.70"
    username = 'root'
    password = 'AkueMax@2022'

    print("Connexion au serveur SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=30)

    print("=== Host Media Folder Permissions ===")
    stdin, stdout, stderr = ssh.exec_command("ls -la /app/media/")
    print(stdout.read().decode())

    print("=== Host Properties Media Folder Permissions ===")
    stdin, stdout, stderr = ssh.exec_command("ls -la /app/media/properties/ | head -n 30")
    print(stdout.read().decode())

    print("=== Container Web Media Folder Permissions ===")
    stdin, stdout, stderr = ssh.exec_command("docker compose -f /app/docker-compose.yml exec -T web ls -la /app/media/properties/ | head -n 30")
    print(stdout.read().decode())

    ssh.close()

if __name__ == "__main__":
    main()
