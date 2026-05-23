import paramiko

def main():
    host = "157.180.127.70"
    port = 22
    username = "root"
    import os
    import sys
    password = os.environ.get("VPS_PASSWORD")
    if not password:
        print("Error: VPS_PASSWORD environment variable is not set.")
        sys.exit(1)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, port=port, username=username, password=password, timeout=10)
        
        commands = [
            ("Host Nginx status", "systemctl status nginx || echo 'No system Nginx'"),
            ("Host Nginx sites", "ls -la /etc/nginx/sites-enabled/ || echo 'No sites-enabled'"),
            ("Host Nginx config for logertogo", "cat /etc/nginx/sites-enabled/logertogo.com || cat /etc/nginx/sites-enabled/default || echo 'None'"),
            ("Active docker compose logs nginx", "docker compose -f /app/docker-compose.yml logs --tail 20 nginx")
        ]
        
        for name, cmd in commands:
            print(f"\n================ {name} ================")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print("".join(stdout.readlines()))
            err = "".join(stderr.readlines())
            if err:
                print("STDERR:")
                print(err)
                
    except Exception as e:
        print(f"Error checking status: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
