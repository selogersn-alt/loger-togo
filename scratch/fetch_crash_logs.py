import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)

print("Fetching docker logs for 'web' container...")
stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose logs --tail=50 web")
logs = stdout.read().decode('utf-8')
err_logs = stderr.read().decode('utf-8')

print("=== LOGS ===")
print(logs)
if err_logs:
    print("=== ERRORS ===")
    print(err_logs)

ssh.close()
