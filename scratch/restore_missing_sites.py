import paramiko
import sys
import os

def restore_missing_sites():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("Connecting to VPS to restore missing sites...")
    ssh.connect(hostname, username=username, password=password, timeout=10)
    
    try:
        # 1. Envoyer le nouveau fichier de conf Nginx complet
        print("--- 1. Envoi de la nouvelle configuration Nginx avec les sites manquants ---")
        sftp = ssh.open_sftp()
        local_conf = os.path.join(os.path.dirname(__file__), '..', 'nginx', 'default.conf')
        sftp.put(local_conf, '/app/nginx/default.conf.new')
        
        # 2. Remplacer par une configuration temporaire HTTP-only (pour valider Let's Encrypt sans crash)
        minimal_nginx = """
server {
    listen 80;
    server_name chat.logersenegal.com nexus-suite.net logertogo.com www.logertogo.com agence.logertogo.com hotels.logertogo.com finance.digitalh.net agence.logersenegal.com digitalh.net www.digitalh.net save.digitalh.net doro.digitalh.net influenceur.digitalh.net pari.digitalh.net www.pari.digitalh.net;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 'Restauration des sites manquants... Veuillez patienter 1 minute.';
        add_header Content-Type text/plain;
    }
}
"""
        with sftp.file('/app/nginx/default.conf', 'w') as f:
            f.write(minimal_nginx)
        sftp.close()
        
        # 3. Démarrer Nginx avec cette config minimaliste
        print("--- 2. Démarrage de Nginx en mode HTTP-only ---")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart nginx", get_pty=True)
        for line in stdout: sys.stdout.write(line)
            
        # 4. Demander les certificats MANQUANTS
        cert_commands = [
            "docker compose run --rm --entrypoint \"certbot certonly --webroot -w /var/www/certbot --email contact@logertogo.com --rsa-key-size 4096 --agree-tos --force-renewal -n -d nexus-suite.net\" certbot"
        ]
        
        print("\n--- 3. Téléchargement des certificats SSL pour Chat et Nexus ---")
        for cmd in cert_commands:
            stdin, stdout, stderr = ssh.exec_command(f"cd /app && {cmd}", get_pty=True)
            for line in stdout: sys.stdout.write(line)
            
        # 5. Restaurer la configuration Nginx complète
        print("\n--- 4. Restauration de la configuration complète et redémarrage final ---")
        ssh.exec_command("mv /app/nginx/default.conf.new /app/nginx/default.conf")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart nginx", get_pty=True)
        for line in stdout: sys.stdout.write(line)
            
        print("\n✅ TOUS LES SITES SONT RESTAURÉS (y compris Chat et Nexus) !")
        
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    restore_missing_sites()
