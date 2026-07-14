import paramiko
import urllib.request
import urllib.error
import socket
import ssl
import sys

# Configuration
VPS_HOST = '157.180.127.70'
VPS_USER = 'root'
VPS_PASS = 'AkueMax@2022'

SITES = [
    {"name": "Agence Loger Sénégal", "url": "https://agence.logersenegal.com", "host_header": "agence.logersenegal.com", "local_port": 8081},
    {"name": "LogerToGo Main", "url": "https://logertogo.com", "host_header": "logertogo.com", "local_port": 80},
    {"name": "LogerToGo Agence", "url": "https://agence.logertogo.com", "host_header": "agence.logertogo.com", "local_port": 80},
    {"name": "LogerToGo Hotels", "url": "https://hotels.logertogo.com", "host_header": "hotels.logertogo.com", "local_port": 80},
    {"name": "H-Finance", "url": "https://finance.digitalh.net", "host_header": "finance.digitalh.net", "local_port": 8090},
    {"name": "Pari Get", "url": "https://pari.digitalh.net", "host_header": "pari.digitalh.net", "local_port": 8095},
    {"name": "DigitalH Site", "url": "https://digitalh.net", "host_header": "digitalh.net", "local_port": 3015},
    {"name": "Save / Telechargeur", "url": "https://save.digitalh.net", "host_header": "save.digitalh.net", "local_port": 13000},
    {"name": "Doro Caviar", "url": "https://doro.digitalh.net", "host_header": "doro.digitalh.net", "local_port": 287}, # Stopped in previous checks
    {"name": "Influenceur / AI Studio", "url": "https://influenceur.digitalh.net", "host_header": "influenceur.digitalh.net", "local_port": 3005}
]

def check_external_url(url):
    """Checks the URL from the local machine (external check)."""
    # Disable SSL verification for check if needed (e.g. self-signed certs)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            return f"UP (HTTP {response.getcode()})"
    except urllib.error.HTTPError as e:
        return f"UP (HTTP {e.code})"
    except urllib.error.URLError as e:
        return f"DOWN ({e.reason})"
    except socket.timeout:
        return "DOWN (Timeout)"
    except Exception as e:
        return f"DOWN ({type(e).__name__})"

def main():
    print("=" * 60)
    print("      VPS WEBSITE DIAGNOSTIC & STATUS AUDIT TOOL")
    print("=" * 60)
    
    # 1. External Check
    print("\nPhase 1: Performing External Internet Reachability Checks...")
    external_results = {}
    for site in SITES:
        print(f"  Checking {site['name']} ({site['url']})...", end="", flush=True)
        status = check_external_url(site['url'])
        print(f" {status}")
        external_results[site['name']] = status

    # 2. SSH Check
    print("\nPhase 2: Connecting to VPS via SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASS, timeout=15)
        print("  [OK] Connected successfully to Hetzner VPS!")
        
        # Check system resource usage
        print("\n=== System Resource Info ===")
        stdin, stdout, stderr = ssh.exec_command("free -h && df -h /")
        print(stdout.read().decode('utf-8'))
        
        # Check running docker containers
        print("=== Docker Containers Status ===")
        stdin, stdout, stderr = ssh.exec_command("docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}'")
        print(stdout.read().decode('utf-8'))
        
        # Check internal routing for each site
        print("=== Internal Nginx/Docker Routing Checks (via Curl inside VPS) ===")
        internal_results = {}
        for site in SITES:
            # We curl localhost with the Host header
            cmd = f"curl -k -I -s -o /dev/null -w '%{{http_code}}' -H 'Host: {site['host_header']}' http://127.0.0.1"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            code = stdout.read().decode('utf-8').strip()
            
            # If code is 000, let's try direct port curl if local_port is set
            port_code = "N/A"
            if site['local_port'] and site['local_port'] != 80:
                cmd_port = f"curl -k -I -s -o /dev/null -w '%{{http_code}}' http://127.0.0.1:{site['local_port']}"
                stdin, stdout, stderr = ssh.exec_command(cmd_port)
                port_code = stdout.read().decode('utf-8').strip()
            
            internal_results[site['name']] = {"nginx": code, "container": port_code}
            print(f"  {site['name']:<28} | Host Nginx response: {code} | Direct port {site['local_port']}: {port_code}")
            
        # 3. Final Summary Report
        print("\n" + "=" * 80)
        print(f"{'SITE NAME':<25} | {'EXTERNAL STATUS':<18} | {'NGINX PORT 80':<15} | {'CONTAINER PORT':<15}")
        print("=" * 80)
        for site in SITES:
            name = site['name']
            ext = external_results[name]
            inte = internal_results.get(name, {"nginx": "Error", "container": "Error"})
            print(f"{name:<25} | {ext:<18} | HTTP {inte['nginx']:<11} | HTTP {inte['container']:<11}")
        print("=" * 80)
        
    except socket.timeout:
        print(f"\n[ERROR] SSH connection to {VPS_HOST}:22 timed out!")
        print("  - The VPS is likely turned off (Off) or frozen.")
        print("  - Or a network-level firewall is blocking port 22.")
    except Exception as e:
        print(f"\n[ERROR] Failed to connect or run diagnostics: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
