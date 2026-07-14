import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def fix_server():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        
        print("Clearing Django cache...")
        cmd_cache = 'cd /app && docker compose exec -T web python manage.py shell -c "from django.core.cache import cache; cache.clear()"'
        stdin, stdout, stderr = ssh.exec_command(cmd_cache)
        print(stdout.read().decode())
        
        print("Re-running the blog post creation script directly...")
        # We will write the script directly inside the container or host
        script = """import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from blog.models import Post, Category, Tag
from users.models import User

author = User.objects.filter(is_superuser=True).first()
if not author: author = User.objects.first()

cat, _ = Category.objects.get_or_create(name='Guides & Conseils')
tag1, _ = Tag.objects.get_or_create(name='Immobilier Togo')

# Just create a simple post to verify it works
post, created = Post.objects.get_or_create(
    title='Pourquoi investir dans l immobilier à Lomé en 2026 ?',
    defaults={
        'author': author,
        'category': cat,
        'status': 'PUBLISHED',
        'content': '<p>Texte de base</p>',
        'featured_image': 'blog/posts/2026/05/invest_lome.png'
    }
)
print('Blog post created/verified!')
"""
        # Execute python code directly via stdin
        cmd_python = "cd /app && docker compose exec -T web python -c \"$(cat << 'EOF'\n" + script + "\nEOF\n)\""
        stdin, stdout, stderr = ssh.exec_command(cmd_python)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_server()
