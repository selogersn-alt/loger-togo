import paramiko
import sys

host = "157.180.127.70"
port = 22
username = "root"
password = "AkueMax@2022"

print(f"Connexion au serveur {host}...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port=port, username=username, password=password, timeout=30)
    print("Connecte!\n")

    # Upload the diagnostic script first
    sftp = ssh.open_sftp()
    sftp.put("scratch/remote_diag.py", "/tmp/remote_diag.py")
    sftp.close()
    print("Script uploade dans /tmp/remote_diag.py")

    # Run it with manage.py shell
    cmd = "cd /app && docker compose exec -T web python manage.py shell < /tmp/remote_diag.py"
    print(f"Execution: {cmd}\n")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    print("=== STDOUT ===")
    print(out)
    if err:
        print("\n=== STDERR ===")
        print(err)

    # Also get the full traceback from gunicorn/django error logs
    print("\n\n=== LOGS DJANGO COMPLETS (500 errors) ===")
    cmd2 = "cd /app && docker compose logs web --since=30m 2>&1 | grep -A 20 'Internal Server Error' | head -100"
    stdin2, stdout2, stderr2 = ssh.exec_command(cmd2, timeout=30)
    stdout2.channel.recv_exit_status()
    out2 = stdout2.read().decode('utf-8', errors='replace').strip()
    err2 = stderr2.read().decode('utf-8', errors='replace').strip()
    print(out2 or "(Aucun log d'erreur 500 recent trouve)")
    if err2:
        print("STDERR:", err2)

    # Check if there's a django error log file
    print("\n\n=== FICHIERS LOGS DJANGO ===")
    cmd3 = "find /app -name '*.log' -type f 2>/dev/null | head -10"
    stdin3, stdout3, stderr3 = ssh.exec_command(cmd3, timeout=15)
    stdout3.channel.recv_exit_status()
    out3 = stdout3.read().decode('utf-8', errors='replace').strip()
    print(out3 or "Aucun fichier .log trouve")

except Exception as e:
    print(f"Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    ssh.close()
