import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def check_s3():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        
        script = """import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()
from django.conf import settings
from blog.models import Post

print(f"USE_S3 is: {getattr(settings, 'USE_S3', False)}")
p = Post.objects.first()
if p and p.featured_image:
    print(f"First post image URL: {p.featured_image.url}")
else:
    print("No post found with image")
"""
        cmd = "cd /app && docker compose exec -T web python -c \"$(cat << 'EOF'\n" + script + "\nEOF\n)\""
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print("STDOUT:", stdout.read().decode())
        print("STDERR:", stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_s3()
