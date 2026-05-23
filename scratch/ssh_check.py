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
        stdin, stdout, stderr = ssh.exec_command("cd /app && git log -n 1")
        print("".join(stdout.readlines()))
    except Exception as e:
        print(f"Error checking status: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
