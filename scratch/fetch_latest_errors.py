import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"Connecting to {host}...")
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
    print("Connected successfully!")

    print("\nFetching latest Gunicorn/Django logs for 500 errors...")
    stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose logs web --tail=150")
    logs = stdout.read().decode('utf-8', 'replace')
    
    with open("scratch/latest_500_error.txt", "w", encoding="utf-8") as f:
        f.write(logs)
        
    print("LOGS SAVED TO scratch/latest_500_error.txt.")
    
    # Print the traceback if found
    if "Traceback" in logs:
        print("\nFound Traceback in logs:")
        tb_index = logs.rfind("Traceback")
        print(logs[tb_index:tb_index+2000])
    else:
        print("\nNo Traceback found in the tail logs. Here is the last 50 lines:")
        lines = logs.split('\n')
        print('\n'.join(lines[-50:]))

except Exception as e:
    print(f"Error: {e}")
finally:
    ssh.close()
