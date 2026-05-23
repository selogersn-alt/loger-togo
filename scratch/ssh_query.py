import paramiko

def main():
    host = "157.180.127.70"
    port = 22
    username = "root"
    import os
    import sys
    password = os.environ.get("VPS_PASSWORD")
    
    if not password:
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            env_path = os.path.join(project_root, ".env")
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("VPS_PASSWORD="):
                            password = line.split("VPS_PASSWORD=", 1)[1].strip().strip('"').strip("'")
                            break
        except Exception:
            pass

    if not password:
        print("Error: VPS_PASSWORD environment variable is not set and no .env found.")
        sys.exit(1)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(host, port=port, username=username, password=password, timeout=10)
        
        commands = [
            "cd /app && docker compose exec -T web python manage.py shell -c \"from django.test import RequestFactory; from django.urls import resolve; rf = RequestFactory(); request = rf.get('/', HTTP_HOST='agence.logertogo.com'); request.urlconf = 'logertogo.urls_agence'; match = resolve('/', urlconf='logertogo.urls_agence'); print('Resolved:', match.func); response = match.func(request, *match.args, **match.kwargs); print('Success status:', response.status_code)\""
        ]
        
        for cmd in commands:
            print(f"\n================ Running: {cmd} ================")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            out_str = "".join(stdout.readlines())
            print(out_str.encode('ascii', 'replace').decode('ascii'))
            err = "".join(stderr.readlines())
            if err:
                print("STDERR:")
                print(err.encode('ascii', 'replace').decode('ascii'))
                
    except Exception as e:
        print(f"Error checking status: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
