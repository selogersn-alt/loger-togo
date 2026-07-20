import paramiko
import sys
import os

def deploy_fixes():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("Connecting to VPS to apply fixes...")
    ssh.connect(hostname, username=username, password=password, timeout=10)
    
    try:
        sftp = ssh.open_sftp()
        local_base = os.path.dirname(os.path.dirname(__file__))
        
        # Uploading nginx
        print("Uploading nginx/default.conf...")
        sftp.put(os.path.join(local_base, 'nginx', 'default.conf'), '/app/nginx/default.conf')
        
        # Uploading models, serializers, views and utils
        print("Uploading logersn/models.py, serializers.py, views.py, utils.py...")
        sftp.put(os.path.join(local_base, 'logersn', 'models.py'), '/app/logersn/models.py')
        sftp.put(os.path.join(local_base, 'logersn', 'serializers.py'), '/app/logersn/serializers.py')
        sftp.put(os.path.join(local_base, 'logersn', 'views.py'), '/app/logersn/views.py')
        sftp.put(os.path.join(local_base, 'logersn', 'utils.py'), '/app/logersn/utils.py')
        
        # Uploading main app urls and views
        print("Uploading logertogo/urls.py and logertogo/views.py...")
        sftp.put(os.path.join(local_base, 'logertogo', 'urls.py'), '/app/logertogo/urls.py')
        sftp.put(os.path.join(local_base, 'logertogo', 'views.py'), '/app/logertogo/views.py')
        
        # Uploading templates
        print("Uploading templates...")
        sftp.put(os.path.join(local_base, 'templates', 'dashboard.html'), '/app/templates/dashboard.html')
        sftp.put(os.path.join(local_base, 'templates', 'payment_request_sent.html'), '/app/templates/payment_request_sent.html')
        sftp.put(os.path.join(local_base, 'templates', 'payment_success.html'), '/app/templates/payment_success.html')
        sftp.put(os.path.join(local_base, 'templates', 'checkout.html'), '/app/templates/checkout.html')
        
        sftp.close()
        
        # Run migrations and restart
        print("Restarting Nginx to apply 413 fix...")
        ssh.exec_command("cd /app && docker compose restart nginx")
        
        print("Applying Database Migrations...")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web python manage.py makemigrations logersn", get_pty=True)
        for line in stdout: sys.stdout.write(line)
        
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web python manage.py migrate", get_pty=True)
        for line in stdout: sys.stdout.write(line)
        
        print("Restarting Web app...")
        ssh.exec_command("cd /app && docker compose restart web")
        
        print("\n✅ TOUT EST RÉPARÉ ET EN LIGNE !")
        
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_fixes()
