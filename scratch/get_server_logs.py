import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose logs --tail=100 web")
    logs = stdout.read().decode('utf-8')
    err_logs = stderr.read().decode('utf-8')
    
    with open("scratch/server_error.log", "w", encoding="utf-8") as f:
        f.write("STDOUT:\n")
        f.write(logs)
        f.write("\nSTDERR:\n")
        f.write(err_logs)
    print("Logs sauvegardés dans scratch/server_error.log ! Veuillez lire ce fichier.")
except Exception as e:
    print(f"Erreur de connexion : {e}")
finally:
    ssh.close()
