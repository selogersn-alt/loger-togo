import paramiko
import time

def deploy_to_hetzner():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    print("Connecting to Hetzner server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=10)
        print("Connected successfully!")
        
        # Commands to run
        commands = [
            "cd /app && git pull origin main",
            "cd /app && docker compose up -d --build web",
            "cd /app && docker compose exec web python manage.py migrate",
            "cd /app && docker compose exec web python scripts/populate_templates.py",
            "cd /app && docker compose restart web",
            "cd /app && docker compose restart nginx"
        ]
        
        for command in commands:
            print(f"Executing: {command}")
            stdin, stdout, stderr = ssh.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            
            out = stdout.read().decode('utf-8')
            err = stderr.read().decode('utf-8')
            
            if out:
                print(f"STDOUT:\n{out}")
            if err:
                print(f"STDERR:\n{err}")
                
            if exit_status != 0:
                print(f"Command failed with status {exit_status}")
                return False
                
        print("Deployment completed successfully!")
        return True
        
    except Exception as e:
        print(f"Connection or execution failed: {str(e)}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_to_hetzner()
