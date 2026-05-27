import sys
import paramiko

def main():
    host = "157.180.127.70"
    port = 22
    username = "root"
    password = "AkueMax@2022"

    print(f"Connexion au serveur {host}:{port}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(host, port=port, username=username, password=password, timeout=30)
        print("Connecté avec succès !\n")

        commands = [
            ("Git pull latest code", "cd /app && git reset --hard && git pull origin main"),
            ("Apply migrations", "cd /app && docker compose exec -T web python manage.py migrate --noinput"),
            ("Collect static files", "cd /app && docker compose exec -T web python manage.py collectstatic --noinput"),
            ("Restart web service", "cd /app && docker compose restart web"),
        ]

        for label, cmd in commands:
            print(f"{'='*60}")
            print(f"[{label}]")
            print(f"CMD: {cmd}")
            print(f"{'='*60}")
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
            exit_code = stdout.channel.recv_exit_status()

            out = stdout.read().decode('utf-8', errors='replace').strip()
            err = stderr.read().decode('utf-8', errors='replace').strip()

            if out:
                print("STDOUT:")
                print(out)
            if err:
                print("STDERR:")
                print(err)

            if exit_code != 0:
                print(f"\n[ERREUR] La commande a echoue (exit code {exit_code})")
            else:
                print(f"\n[OK] Etape terminee avec succes !")
            print()

        print("Deploiement termine avec succes !")

    except Exception as e:
        print(f"Erreur durant le deploiement: {e}")
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
