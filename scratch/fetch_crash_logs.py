import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)

print("Fetching Gunicorn crash logs...")
stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose logs web --tail=100")
out = stdout.read().decode('utf-8', 'replace')
err = stderr.read().decode('utf-8', 'replace')

with open("scratch/crash_logs.txt", "w", encoding="utf-8") as f:
    f.write("STDOUT:\n" + out + "\nSTDERR:\n" + err)

print("CRASH LOGS SAVED.")
ssh.close()
