import paramiko
import os

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("Connecting...")
try:
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
    print("Connected!")
    
    cmd = "cd /app && docker compose logs web --tail=1000 2>&1"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    logs = stdout.read().decode('utf-8', errors='replace')
    log_file_path = os.path.join(os.path.dirname(__file__), "web_logs.txt")
    with open(log_file_path, "w", encoding="utf-8") as f:
        f.write(logs)
    print(f"SUCCESS: Logs written to {log_file_path}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
