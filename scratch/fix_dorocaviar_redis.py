import paramiko
import sys
import time

host = "157.180.127.70"
port = 22
username = "root"
password = "AkueMax@2022"

print(f"Connecting to {host} to secure Dorocaviar Redis...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port=port, username=username, password=password, timeout=30)
    print("Connected successfully!\n")

    secure_cmd = """
    echo "Locating the dorocaviar project directory..."
    # Get the working directory of the container
    PROJECT_DIR=$(docker inspect dorocaviar_redis --format '{{ index .Config.Labels "com.docker.compose.project.working_dir" }}')
    
    if [ -z "$PROJECT_DIR" ]; then
        echo "Could not find the project directory for dorocaviar_redis."
        exit 1
    fi
    
    echo "Found project at: $PROJECT_DIR"
    
    # Check if docker-compose.yml or docker-compose.yaml exists
    COMPOSE_FILE=""
    if [ -f "$PROJECT_DIR/docker-compose.yml" ]; then
        COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
    elif [ -f "$PROJECT_DIR/docker-compose.yaml" ]; then
        COMPOSE_FILE="$PROJECT_DIR/docker-compose.yaml"
    else
        echo "Could not find docker-compose file in $PROJECT_DIR"
        exit 1
    fi
    
    echo "Backing up $COMPOSE_FILE..."
    cp "$COMPOSE_FILE" "$COMPOSE_FILE.bak"
    
    echo "Securing Redis ports in $COMPOSE_FILE..."
    # Use sed to replace port mapping 6379:6379 with 127.0.0.1:6379:6379
    # We will replace lines that contain '6379:6379'
    sed -i 's/- "6379:6379"/- "127.0.0.1:6379:6379"/g' "$COMPOSE_FILE"
    sed -i "s/- '6379:6379'/- '127.0.0.1:6379:6379'/g" "$COMPOSE_FILE"
    sed -i 's/- 6379:6379/- 127.0.0.1:6379:6379/g' "$COMPOSE_FILE"
    
    echo "Applying new configuration..."
    cd "$PROJECT_DIR"
    docker compose up -d
    
    echo "Checking new exposed ports..."
    docker ps --format "{{.ID}} {{.Names}} {{.Ports}}" | grep "dorocaviar_redis"
    """

    stdin, stdout, stderr = ssh.exec_command(secure_cmd)
    
    while not stdout.channel.exit_status_ready():
        time.sleep(0.5)

    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()

    if out:
        print(out)
    if err:
        print("ERRORS:")
        print(err)

    print("\nDorocaviar Redis secured!")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    ssh.close()
