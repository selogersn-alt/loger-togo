import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)

stdin, stdout, stderr = ssh.exec_command("ls -la /app/management/migrations/")
print("MIGRATIONS DIR:")
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
