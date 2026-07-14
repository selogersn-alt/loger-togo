import paramiko
import os
import time

HOST = "157.180.127.70"
USER = "root"
PASSWORD = "AkueMax@2022"

def main():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=60)
        print("Connected successfully!")
        
        # 1. Back up existing configuration on VPS
        print("\n1. Backing up existing /app/nginx/default.conf on VPS...")
        stdin, stdout, stderr = ssh.exec_command("cp /app/nginx/default.conf /app/nginx/default.conf.bak")
        err = stderr.read().decode().strip()
        if err:
            print(f"  Backup warning/error: {err}")
        else:
            print("  Backup created at /app/nginx/default.conf.bak")
            
        # 2. Upload the new configuration
        print("\n2. Uploading corrected default.conf to VPS...")
        sftp = ssh.open_sftp()
        local_path = "nginx/default.conf"
        remote_path = "/app/nginx/default.conf"
        sftp.put(local_path, remote_path)
        sftp.close()
        print("  Upload successful!")
        
        # 3. Test Nginx configuration in container
        print("\n3. Testing Nginx configuration in container...")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T nginx nginx -t")
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        print("  STDOUT:")
        print(out)
        print("  STDERR:")
        print(err)
        
        if "successful" in err.lower() or "successful" in out.lower() or "syntax is ok" in err.lower() or "syntax is ok" in out.lower():
            # 4. Reload Nginx configuration
            print("\n4. Reloading Nginx configuration...")
            stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T nginx nginx -s reload")
            out_reload = stdout.read().decode().strip()
            err_reload = stderr.read().decode().strip()
            if out_reload:
                print(f"  STDOUT: {out_reload}")
            if err_reload:
                print(f"  STDERR: {err_reload}")
            print("  Nginx reloaded successfully!")
        else:
            print("\nWARNING: Nginx configuration test FAILED! Rolling back...")
            stdin, stdout, stderr = ssh.exec_command("cp /app/nginx/default.conf.bak /app/nginx/default.conf")
            print("  Rollback completed. Please verify the configuration locally.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()
        print("\nFINISHED!")

if __name__ == "__main__":
    main()
