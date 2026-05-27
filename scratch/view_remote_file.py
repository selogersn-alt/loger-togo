import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Connecting to {host}...")
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
    print("Connected successfully!")

    print("\nReading /app/management/models.py lines 65-75 on host VPS...")
    stdin, stdout, stderr = ssh.exec_command("sed -n '65,75p' /app/management/models.py")
    print(stdout.read().decode('utf-8', 'replace'))

    print("\nReading /app/management/models.py lines 65-75 INSIDE running container...")
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web sed -n '65,75p' /app/management/models.py")
    print(stdout.read().decode('utf-8', 'replace'))

    print("\nChecking file size and md5sum of local vs remote:")
    import hashlib
    local_md5 = hashlib.md5(open(r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\management\models.py", "rb").read()).hexdigest()
    print(f"Local MD5: {local_md5}")
    
    stdin, stdout, stderr = ssh.exec_command("md5sum /app/management/models.py")
    print(f"Remote Host MD5: {stdout.read().decode('utf-8').strip()}")

    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web md5sum /app/management/models.py")
    print(f"Remote Container MD5: {stdout.read().decode('utf-8').strip()}")

except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
