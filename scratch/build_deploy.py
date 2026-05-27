import paramiko
import time
import sys

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Connecting to {host}...")
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=60)
    print("Connected successfully!")

    print("\n1. Rebuilding web service container with the uploaded hotfix files...")
    # docker compose up -d --build web
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose up -d --build web")
    
    # We must print stdout/stderr as it comes
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            print(stdout.channel.recv(1024).decode('utf-8', 'replace'), end='')
        if stderr.channel.recv_stderr_ready():
            print(stderr.channel.recv_stderr(1024).decode('utf-8', 'replace'), end='', file=sys.stderr)
        time.sleep(0.5)
    
    print(stdout.read().decode('utf-8', 'replace'))
    print(stderr.read().decode('utf-8', 'replace'))

    print("\n2. Checking web container status...")
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose ps web")
    print(stdout.read().decode())

    print("\n3. Waiting 5 seconds and checking Gunicorn logs...")
    time.sleep(5)
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose logs web --tail=50")
    print(stdout.read().decode('utf-8', 'replace'))

except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
    print("\nFINISHED!")
