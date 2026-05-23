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
            "echo '--- DOCKER CONTAINERS ---' && docker ps",
            "echo '--- COMPOSE CONFIG ---' && grep -A 10 nginx /app/docker-compose.yml",
            "echo '--- NGINX ACTIVE CONFIG ---' && docker compose -f /app/docker-compose.yml exec nginx cat /etc/nginx/conf.d/default.conf",
            "echo '--- CERTBOT CERTIFICATES ---' && docker compose -f /app/docker-compose.yml run --rm certbot certificates"
        ]
        
        for cmd in commands:
            print(f"\n================ Running: {cmd} ================")
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
