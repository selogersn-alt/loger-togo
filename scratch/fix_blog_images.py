import paramiko
import os

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

IMG_INVEST = r"C:\Users\mursd\.gemini\antigravity-ide\brain\1170fcec-a1ef-4c15-a41a-c47daebedddb\invest_lome_1780154067696.png"
IMG_DOCS = r"C:\Users\mursd\.gemini\antigravity-ide\brain\1170fcec-a1ef-4c15-a41a-c47daebedddb\docs_location_1780154082875.png"
IMG_AGENCY = r"C:\Users\mursd\.gemini\antigravity-ide\brain\1170fcec-a1ef-4c15-a41a-c47daebedddb\agency_lome_1780154095550.png"

def deploy_images_to_docker_volume():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to server...")
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        
        print("Creating temporary directory on host...")
        ssh.exec_command("mkdir -p /app/tmp_media")
        
        print("Uploading images via SFTP to host tmp_media...")
        sftp = ssh.open_sftp()
        sftp.put(IMG_INVEST, "/app/tmp_media/invest_lome.png")
        sftp.put(IMG_DOCS, "/app/tmp_media/docs_location.png")
        sftp.put(IMG_AGENCY, "/app/tmp_media/agency_lome.png")
        sftp.close()
            
        print("Creating directories inside the Docker Volume...")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web mkdir -p /app/media/blog/posts/2026/05")
        stdout.read() # wait
        
        print("Copying files from host to the Docker container's volume...")
        commands = [
            "cd /app && docker compose cp /app/tmp_media/invest_lome.png web:/app/media/blog/posts/2026/05/invest_lome.png",
            "cd /app && docker compose cp /app/tmp_media/docs_location.png web:/app/media/blog/posts/2026/05/docs_location.png",
            "cd /app && docker compose cp /app/tmp_media/agency_lome.png web:/app/media/blog/posts/2026/05/agency_lome.png",
            "cd /app && docker compose exec -T web chown -R 999:999 /app/media/blog",
            "cd /app && docker compose exec -T web chmod -R 755 /app/media/blog"
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.read() # block until finished
            err = stderr.read().decode('utf-8', 'replace')
            if err:
                print(f"Warning/Error on '{cmd}': {err}")
                
        print("Cleaning up temporary host files...")
        ssh.exec_command("rm -rf /app/tmp_media")
            
        print("Images ont été injectées avec succès dans le volume Docker !")
        
    except Exception as e:
        print(f"Connection Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_images_to_docker_volume()
