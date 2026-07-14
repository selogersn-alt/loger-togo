import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def upload_to_s3():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        
        script = """import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

images = [
    'blog/posts/2026/05/invest_lome.png',
    'blog/posts/2026/05/docs_location.png',
    'blog/posts/2026/05/agency_lome.png'
]

for img_name in images:
    local_path = f"/app/media/{img_name}"
    print(f"Uploading {img_name} to Cloudflare R2...")
    
    if not os.path.exists(local_path):
        print(f"Error: {local_path} does not exist locally.")
        continue
        
    with open(local_path, 'rb') as f:
        file_content = f.read()
        
    # Delete if exists to avoid renaming
    if default_storage.exists(img_name):
        print(f"File {img_name} already exists in R2, deleting...")
        default_storage.delete(img_name)
        
    # Save to R2
    saved_name = default_storage.save(img_name, ContentFile(file_content))
    print(f"Successfully uploaded to S3: {saved_name}")
"""
        print("Uploading images from Docker volume to Cloudflare R2 (S3)...")
        cmd = "cd /app && docker compose exec -T web python -c \"$(cat << 'EOF'\n" + script + "\nEOF\n)\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print("STDERR:", err)
            
        print("Opération S3 terminée !")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    upload_to_s3()
