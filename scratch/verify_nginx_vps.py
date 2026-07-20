import paramiko
import sys

def verify_nginx_vps():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password, timeout=10)
    
    print("--- Vérification du fichier default.conf sur le VPS ---")
    stdin, stdout, stderr = ssh.exec_command("cat /app/nginx/default.conf | grep -A 5 nexus-suite", get_pty=True)
    for line in stdout: sys.stdout.write(line)
        
    print("\n--- Vérification de l'état de Nginx ---")
    stdin, stdout, stderr = ssh.exec_command("docker ps | grep nginx", get_pty=True)
    for line in stdout: sys.stdout.write(line)
        
    ssh.close()

if __name__ == "__main__":
    verify_nginx_vps()
