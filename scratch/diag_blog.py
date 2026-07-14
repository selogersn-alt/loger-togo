import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def check_blogs():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        
        script = """import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()
from blog.models import Post

for p in Post.objects.all()[:3]:
    print("---")
    print(f"Title: {p.title}")
    if p.featured_image:
        print(f"Image Name: {p.featured_image.name}")
        try:
            print(f"Image URL: {p.featured_image.url}")
        except Exception as e:
            print(f"Image URL Error: {e}")
        import os
        path = p.featured_image.path
        print(f"Image Path: {path}")
        print(f"Exists on disk? {os.path.exists(path)}")
    else:
        print("No image.")
"""
        cmd = "cd /app && docker compose exec -T web python -c \"$(cat << 'EOF'\n" + script + "\nEOF\n)\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print("STDERR:", err)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_blogs()
