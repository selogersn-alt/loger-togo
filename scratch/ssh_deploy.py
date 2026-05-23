import sys
import paramiko

def main():
    host = "157.180.127.70"
    port = 22
    username = "root"
    import os
    
    # 1. Try to read from environment variable
    password = os.environ.get("VPS_PASSWORD")
    
    # 2. Try to read from local .env file (which is in .gitignore)
    if not password:
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            env_path = os.path.join(project_root, ".env")
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("VPS_PASSWORD="):
                            password = line.split("VPS_PASSWORD=", 1)[1].strip().strip('"').strip("'")
                            break
        except Exception:
            pass

    if not password:
        print("Error: VPS_PASSWORD is not set in environment or local .env file.")
        sys.exit(1)

    print(f"Connecting to {host}:{port} as {username}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, port=port, username=username, password=password, timeout=30)
        print("Successfully connected!")
        
        # Pull changes and rebuild docker web service
        commands = [
            "cd /app && git reset --hard && git pull origin main",
            "cd /app && docker compose up -d --build web nginx"
        ]
        
        for cmd in commands:
            print(f"\nExecuting: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            
            # Print stdout and stderr in real-time
            for line in stdout:
                print(f"STDOUT: {line.strip()}")
            for line in stderr:
                print(f"STDERR: {line.strip()}")
                
        print("\nDeployment completed successfully!")
        
    except Exception as e:
        print(f"Error during deployment: {e}")
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
