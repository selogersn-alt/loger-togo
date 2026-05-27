import paramiko
import os

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)

files_to_deploy = [
    ("d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\management\\models.py", "/app/management/models.py"),
    ("d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\management\\views_hotel.py", "/app/management/views_hotel.py"),
    ("d:\\HDIGITAL\\ANDROID_ANTIGRAVITY\\LOGERTOGO\\management\\migrations\\0014_remove_hotelbooking_extra_charges.py", "/app/management/migrations/0014_remove_hotelbooking_extra_charges.py")
]

print("Starting FORCE DEPLOY into Docker container...")

for local_path, remote_path in files_to_deploy:
    print(f"Reading {local_path}...")
    with open(local_path, "rb") as f:
        content = f.read()
    
    print(f"Injecting into {remote_path}...")
    # Write to a temp file on host
    host_tmp = f"/tmp/{os.path.basename(remote_path)}"
    sftp = ssh.open_sftp()
    with sftp.file(host_tmp, 'wb') as f:
        f.write(content)
    sftp.close()
    
    # Copy from host into the running container and overwrite the host /app too just in case
    cmd = f"cp {host_tmp} {remote_path} && cd /app && docker compose cp {host_tmp} web:{remote_path}"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.read()  # wait
    
    # Also use docker exec tee as a fallback
    cmd_tee = f"cd /app && cat {host_tmp} | docker compose exec -T web tee {remote_path} > /dev/null"
    ssh.exec_command(cmd_tee)[1].read()

print("Applying migrations...")
stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web python manage.py migrate --noinput")
print(stdout.read().decode())

print("Restarting web container...")
stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart web")
print(stdout.read().decode())

ssh.close()
print("FORCE DEPLOY SUCCESSFUL!")
