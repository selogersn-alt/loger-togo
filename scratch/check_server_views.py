import paramiko
import sys

def check_server_views():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("Connecting to VPS...")
    ssh.connect(hostname, username=username, password=password, timeout=10)
    
    try:
        stdin, stdout, stderr = ssh.exec_command('grep -A 2 -B 2 "redirect.*paiement" /app/logersn/views.py')
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        
        print("=== STDOUT ===")
        print(out)
        print("=== STDERR ===")
        print(err)
        
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    check_server_views()
