import paramiko

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

def main():
    print("Connecting to Hetzner VPS...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        print("Connected successfully!")
        
        sftp = ssh.open_sftp()
        remote_path = "/app/nginx/default.conf"
        local_path = "scratch/vps_default.conf"
        print(f"Downloading {remote_path} to {local_path}...")
        sftp.get(remote_path, local_path)
        sftp.close()
        print("Download successful!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
