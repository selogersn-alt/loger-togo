import paramiko
import sys
import os

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
            ("Docker containers (docker ps)", "docker ps"),
            ("Host Nginx service status", "systemctl status nginx || echo 'No host Nginx'"),
            ("Host Nginx sites enabled", "ls -la /etc/nginx/sites-enabled/ || echo 'No sites-enabled'"),
            ("Host Nginx logertogo.com config", "cat /etc/nginx/sites-enabled/logertogo.com || cat /etc/nginx/sites-available/logertogo.com || echo 'No logertogo host config'"),
            ("Host Nginx default config", "cat /etc/nginx/sites-enabled/default || echo 'No default host config'"),
            ("Docker Nginx config (/app/nginx/default.conf)", "cat /app/nginx/default.conf || echo 'No /app/nginx/default.conf'"),
            ("Docker Nginx SSL config (/app/nginx/default.conf.ssl)", "cat /app/nginx/default.conf.ssl || echo 'No /app/nginx/default.conf.ssl'"),
            ("Local settings on VPS", "cat /app/logertogo/local_settings.py || echo 'No local_settings.py'"),
            ("Nginx container logs", "cd /app && docker compose logs --tail=50 nginx"),
            ("Web container logs", "cd /app && docker compose logs --tail=50 web"),
            ("Curl test direct to Web (Django)", "cd /app && docker compose exec -T web curl -I http://localhost:8000 || curl -I http://localhost:8000"),
            ("Curl test subdomain directly to Web", "curl -I -H 'Host: agence.logertogo.com' http://127.0.0.1:8000"),
            ("Curl test HTTP port 80", "curl -I http://127.0.0.1"),
            ("Curl test HTTPS port 443", "curl -k -I https://127.0.0.1"),
            ("Curl test subdomain HTTP port 80", "curl -I -H 'Host: agence.logertogo.com' http://127.0.0.1"),
            ("Curl test subdomain HTTPS port 443", "curl -k -I -H 'Host: agence.logertogo.com' https://127.0.0.1")
        ]
        
        output_file = "scratch/diagnose_vps_result.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=== VPS DIAGNOSTIC REPORT ===\n\n")
            for name, cmd in commands:
                print(f"Executing: {name}...")
                f.write(f"\n================ {name} ================\n")
                f.write(f"Command: {cmd}\n")
                try:
                    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
                    out = stdout.read().decode('utf-8', errors='replace')
                    err = stderr.read().decode('utf-8', errors='replace')
                    f.write("--- STDOUT ---\n")
                    f.write(out)
                    if err:
                        f.write("--- STDERR ---\n")
                        f.write(err)
                except Exception as e:
                    f.write(f"ERROR executing command: {e}\n")
        print(f"\nDiagnostic completed! Results written to {output_file}")
        
    except Exception as e:
        print(f"SSH Connection Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
