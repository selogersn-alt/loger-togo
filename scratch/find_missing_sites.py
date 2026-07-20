import paramiko
import sys

def find_missing_sites():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password, timeout=10)
    
    print("--- RUNNING DOCKER CONTAINERS ON VPS ---")
    stdin, stdout, stderr = ssh.exec_command("docker ps --format '{{.Names}} - {{.Ports}}'", get_pty=True)
    for line in stdout: sys.stdout.write(line)
        
    ssh.close()

if __name__ == "__main__":
    find_missing_sites()
