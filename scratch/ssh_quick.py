import paramiko
import sys

def main():
    host = "157.180.127.70"
    port = 22
    username = "root"
    import os
    password = os.environ.get("VPS_PASSWORD")
    if not password:
        print("Error: VPS_PASSWORD environment variable is not set.")
        sys.exit(1)

    print("Connecting to VPS...", flush=True)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, port=port, username=username, password=password, timeout=10)
        print("Connected!", flush=True)
        
        commands = [
            ("Docker containers", "docker ps"),
            ("Let's Encrypt live directory", "ls -la /app/certbot/conf/live/"),
            ("Let's Encrypt logertogo.com directory", "ls -la /app/certbot/conf/live/logertogo.com/ || echo 'No logertogo.com directory'"),
            ("Nginx config content", "cat /app/nginx/default.conf"),
            ("Nginx SSL config content", "cat /app/nginx/default.conf.ssl")
        ]
        
        for name, cmd in commands:
            print(f"\n=== {name} ({cmd}) ===", flush=True)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            for line in stdout:
                print(line, end="", flush=True)
            for line in stderr:
                print(f"ERR: {line}", end="", flush=True)
                
    except Exception as e:
        print(f"Error checking status: {e}", flush=True)
    finally:
        ssh.close()
        print("\nDisconnected.", flush=True)

if __name__ == "__main__":
    main()
