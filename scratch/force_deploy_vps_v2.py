import paramiko
import sys

def force_deploy():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    print("Connecting to Hetzner server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=10)
        print("Connected successfully!\n")
        
        # On relance uniquement la fin du processus de déploiement (le pull est déjà fait)
        commands = [
            "cd /app && docker compose up -d --build web",
            "cd /app && docker compose exec web python manage.py migrate",
            "cd /app && docker compose exec web python scripts/populate_templates.py",
            "cd /app && docker compose restart web",
            "cd /app && docker compose restart nginx",
            "cd /app && docker compose logs --tail=20 nginx"
        ]
        
        for command in commands:
            print(f"\n--- Executing: {command} ---")
            stdin, stdout, stderr = ssh.exec_command(command, get_pty=True) # get_pty pour affichage temps réel
            
            # Affichage en temps réel
            for line in iter(stdout.readline, ""):
                sys.stdout.write(line)
                sys.stdout.flush()
                
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                print(f"Command failed with status {exit_status}")
                return False
                
        print("\nDeployment completed successfully!")
        return True
        
    except Exception as e:
        print(f"Connection or execution failed: {str(e)}")
        return False
    finally:
        ssh.close()

if __name__ == "__main__":
    force_deploy()
