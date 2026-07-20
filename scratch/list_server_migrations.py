import paramiko

def run_cmd(ssh, cmd):
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if out:
        print("STDOUT:")
        print(out)
    if err:
        print("STDERR:")
        print(err)
    print("-" * 40)

def main():
    host = "157.180.127.70"
    username = 'root'
    password = 'AkueMax@2022'

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=30)

    print("=== Listing host migrations ===")
    run_cmd(ssh, "ls -la /app/logersn/migrations/")

    print("=== Content of 0036_property_visible_on_portal.py ===")
    run_cmd(ssh, "cat /app/logersn/migrations/0036_property_visible_on_portal.py")
    
    ssh.close()

if __name__ == "__main__":
    main()
