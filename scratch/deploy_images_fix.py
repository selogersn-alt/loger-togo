import paramiko
import os

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

# Local paths for generated images
IMG_INVEST = r"C:\Users\mursd\.gemini\antigravity-ide\brain\1170fcec-a1ef-4c15-a41a-c47daebedddb\invest_lome_1780154067696.png"
IMG_DOCS = r"C:\Users\mursd\.gemini\antigravity-ide\brain\1170fcec-a1ef-4c15-a41a-c47daebedddb\docs_location_1780154082875.png"
IMG_AGENCY = r"C:\Users\mursd\.gemini\antigravity-ide\brain\1170fcec-a1ef-4c15-a41a-c47daebedddb\agency_lome_1780154095550.png"

REMOTE_MEDIA_BLOG = "/app/media/blog/posts/2026/05"

def deploy_images():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print("Connecting to server...")
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        
        print("Creating directory...")
        stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {REMOTE_MEDIA_BLOG}")
        # Wait for command to complete
        out = stdout.read().decode()
        err = stderr.read().decode()
        if err:
            print(f"Directory creation warning/error: {err}")
            
        print("Uploading images via SFTP...")
        sftp = ssh.open_sftp()
        try:
            print(f"Uploading {IMG_INVEST}...")
            sftp.put(IMG_INVEST, f"{REMOTE_MEDIA_BLOG}/invest_lome.png")
            print("Upload 1 OK")
            
            print(f"Uploading {IMG_DOCS}...")
            sftp.put(IMG_DOCS, f"{REMOTE_MEDIA_BLOG}/docs_location.png")
            print("Upload 2 OK")
            
            print(f"Uploading {IMG_AGENCY}...")
            sftp.put(IMG_AGENCY, f"{REMOTE_MEDIA_BLOG}/agency_lome.png")
            print("Upload 3 OK")
        except Exception as upload_err:
            print(f"SFTP Upload Error: {upload_err}")
        finally:
            sftp.close()
            
        print("Fixing file permissions inside the container...")
        stdin, stdout, stderr = ssh.exec_command(f"cd /app && docker compose exec -T web chmod -R 755 /app/media/blog")
        stdout.read() # wait
            
        print("Opération terminée !")
        
    except Exception as e:
        print(f"Connection Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_images()
