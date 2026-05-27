import paramiko, sys

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)

# Get full gunicorn error logs with traceback
cmd = "cd /app && docker compose logs web --tail=200 2>&1"
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
stdout.channel.recv_exit_status()
raw = stdout.read()

# Write raw bytes to file to avoid encoding issues
with open("scratch/prod_logs.txt", "wb") as f:
    f.write(raw)

print("Logs sauvegardes dans scratch/prod_logs.txt")
print(f"Taille: {len(raw)} bytes")

ssh.close()
