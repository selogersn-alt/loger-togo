import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def main():
    print("Connecting to Hetzner VPS...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        print("Connected successfully!")
        
        commands = [
            ("Cat /app/.env", "cat /app/.env || echo 'No /app/.env'"),
            ("Cat /app/docker-compose.yml", "cat /app/docker-compose.yml || echo 'No /app/docker-compose.yml'"),
            ("Django settings evaluation inside container", "cd /app && docker compose exec -T web python -c \"import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings'); import django; django.setup(); from django.conf import settings; print('SECURE_SSL_REDIRECT:', settings.SECURE_SSL_REDIRECT); print('SECURE_PROXY_SSL_HEADER:', settings.SECURE_PROXY_SSL_HEADER); print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS); print('DEBUG:', settings.DEBUG)\""),
            ("Nginx container config validation", "cd /app && docker compose exec -T nginx nginx -T | grep -E 'server_name|listen|proxy_pass|ssl_certificate' || echo 'Failed nginx -T'"),
        ]
        
        for name, cmd in commands:
            print(f"\n--- {name} ---")
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
            out = stdout.read().decode('utf-8', errors='replace')
            err = stderr.read().decode('utf-8', errors='replace')
            print("STDOUT:")
            print(out)
            if err:
                print("STDERR:")
                print(err)
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
