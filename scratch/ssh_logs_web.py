import paramiko
import sys

def main():
    host = "157.180.127.70"
    port = 22
    username = "root"
    import os
    password = os.environ.get("VPS_PASSWORD")
    
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
        print("Error: VPS_PASSWORD environment variable is not set and no .env found.")
        sys.exit(1)

    print("Connecting to VPS to check web container logs...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, port=port, username=username, password=password, timeout=10)
        
        cmd = "docker compose -f /app/docker-compose.yml logs --tail 30 web"
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        # Read and print safely
        out_content = "".join(stdout.readlines())
        err_content = "".join(stderr.readlines())
        
        # Print using utf-8 or replacing errors
        sys.stdout.buffer.write(out_content.encode('utf-8', errors='replace'))
        sys.stdout.buffer.write(b"\n")
        sys.stdout.buffer.write(err_content.encode('utf-8', errors='replace'))
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
