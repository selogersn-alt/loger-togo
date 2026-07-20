import paramiko

def main():
    host = "157.180.127.70"
    username = 'root'
    password = 'AkueMax@2022'

    print("Connexion au serveur SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=30)

    # Simuler la requête en utilisant une expression ternaire valide sur une seule ligne
    django_cmd = (
        "from django.conf import settings; "
        "settings.ALLOWED_HOSTS.append('testserver') if 'testserver' not in settings.ALLOWED_HOSTS else None; "
        "from django.test import RequestFactory; "
        "from logertogo.views import home_view; "
        "rf = RequestFactory(); "
        "req = rf.get('/'); "
        "res = home_view(req); "
        "print('STATUS:', res.status_code); "
        "print('BODY LENGTH:', len(res.content))"
    )

    cmd = f'cd /app && docker compose exec -T web python manage.py shell -c "{django_cmd}"'
    print(f"Exécution de la commande de diagnostic...")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    
    if out:
        print("STDOUT:")
        print(out)
    if err:
        print("STDERR:")
        print(err)
        
    ssh.close()

if __name__ == "__main__":
    main()
