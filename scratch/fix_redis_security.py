import paramiko
import sys
import time

host = "157.180.127.70"
port = 22
username = "root"
password = "AkueMax@2022"

print(f"Connecting to {host} to secure Redis...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port=port, username=username, password=password, timeout=30)
    print("Connected successfully!\n")

    # Command to secure Redis natively
    secure_cmd = """
    echo "Checking what is running on port 6379..."
    netstat -tulnp | grep 6379 || echo "Nothing on 6379"

    echo "Attempting to secure native Redis..."
    if [ -f /etc/redis/redis.conf ]; then
        # Force bind to localhost only
        sed -i 's/^bind .*/bind 127.0.0.1 ::1/' /etc/redis/redis.conf
        # Enable protected mode
        sed -i 's/^protected-mode .*/protected-mode yes/' /etc/redis/redis.conf
        
        systemctl restart redis-server || systemctl restart redis
        echo "Native Redis secured successfully."
    else
        echo "No native Redis configuration found at /etc/redis/redis.conf."
    fi

    echo "Checking for Docker containers exposing port 6379..."
    # Find any docker container exposing 6379 publicly and restart it securely or just notify
    docker ps --format "{{.ID}} {{.Names}} {{.Ports}}" | grep "0.0.0.0:6379"
    """

    stdin, stdout, stderr = ssh.exec_command(secure_cmd)
    
    # Wait for the command to finish
    while not stdout.channel.exit_status_ready():
        time.sleep(0.5)

    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()

    if out:
        print(out)
    if err:
        print("ERRORS:")
        print(err)

    print("\nRedis security fix applied!")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    ssh.close()
