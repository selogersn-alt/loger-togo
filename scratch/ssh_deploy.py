import sys
import paramiko

def main():
    host = "157.180.127.70"
    port = 22
    username = "root"
    password = "AkueMax@2022"

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
