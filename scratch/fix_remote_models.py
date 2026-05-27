import paramiko
import time
import sys

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Connecting to {host}...")
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
    print("Connected successfully!")

    print("\n1. Reading /app/management/models.py from VPS...")
    sftp = ssh.open_sftp()
    with sftp.open("/app/management/models.py", "rb") as f:
        content_bytes = f.read()
    content = content_bytes.decode('utf-8', 'replace')
    
    print("Content read. Checking lines around Lease.unique_ref:")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "def unique_ref" in line:
            print(f"Found unique_ref at line {i+1}:")
            start = max(0, i-3)
            end = min(len(lines), i+3)
            for j in range(start, end):
                print(f"  Line {j+1}: {lines[j]}")

    print("\n2. Fixing the property decorator conflict directly on the VPS...")
    fixed_content = content
    if "import builtins" not in fixed_content:
        fixed_content = "import builtins\n" + fixed_content
        print("Added 'import builtins' to remote content.")
        
    # Replace standard `@property` with `@builtins.property` for unique_refs
    old_lease_pattern = "    @property\n    def unique_ref"
    new_lease_pattern = "    @builtins.property\n    def unique_ref"
    
    if old_lease_pattern in fixed_content:
        fixed_content = fixed_content.replace(old_lease_pattern, new_lease_pattern)
        print("Replaced `@property` with `@builtins.property` for Lease unique_ref!")
    else:
        # Let's do a wider replace just in case of CRLF line endings (\r\n)
        fixed_content = fixed_content.replace("    @property\r\n    def unique_ref", "    @builtins.property\r\n    def unique_ref")
        print("Tried CRLF replacement for unique_ref decorators.")

    # Write the fixed content back to the VPS host file
    with sftp.open("/app/management/models.py", "wb") as f:
        f.write(fixed_content.encode('utf-8'))
    sftp.close()
    print("Successfully wrote fixed models.py back to VPS!")

    print("\n3. Rebuilding the Docker container on VPS...")
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose up -d --build web")
    
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            print(stdout.channel.recv(1024).decode('utf-8', 'replace'), end='')
        if stderr.channel.recv_stderr_ready():
            print(stderr.channel.recv_stderr(1024).decode('utf-8', 'replace'), end='', file=sys.stderr)
        time.sleep(0.5)

    print(stdout.read().decode('utf-8', 'replace'))
    print(stderr.read().decode('utf-8', 'replace'))

    print("\n4. Checking web container logs...")
    time.sleep(5)
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose logs web --tail=50")
    print(stdout.read().decode('utf-8', 'replace'))

except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
    print("\nFINISHED!")
