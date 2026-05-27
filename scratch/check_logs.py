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

    commands = [
        # Get last 100 lines of Django error logs
        ("Logs Django (erreurs recentes)", "cd /app && docker compose logs web --tail=150 2>&1 | grep -E 'Error|Exception|Traceback|500|Internal|AttributeError|TypeError|NameError|ValueError' | tail -80"),
        # Full last 50 log lines (unfiltered)
        ("Derniers logs complets", "cd /app && docker compose logs web --tail=60 2>&1"),
    ]

    for label, cmd in commands:
        print(f"\n{'='*70}")
        print(f"[{label}]")
        print(f"{'='*70}")
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
        stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', errors='replace').strip()
        err = stderr.read().decode('utf-8', errors='replace').strip()
        if out:
            print(out)
        if err:
            print(err)

except Exception as e:
    print(f"Erreur: {e}")
    sys.exit(1)
finally:
    ssh.close()
