import paramiko
import os
import sys

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def deploy_fix():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=60)
        sftp = ssh.open_sftp()
        
        local_file = r"D:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\logersn\views.py"
        remote_file = "/app/logersn/views.py"
        
        print(f"Uploading {local_file} -> {remote_file}...")
        sftp.put(local_file, remote_file)
        
        print("Restarting Docker Web Container...")
        stdin, stdout, stderr = ssh.exec_command('cd /app && docker compose restart web')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        print("Fix deployed successfully!")
        
    except Exception as e:
        print(f"Deployment failed: {e}")
    finally:
        if 'sftp' in locals(): sftp.close()
        ssh.close()

if __name__ == "__main__":
    deploy_fix()
