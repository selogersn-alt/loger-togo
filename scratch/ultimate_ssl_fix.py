import paramiko
import sys

def ultimate_ssl_fix():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("Connecting to VPS for the Ultimate SSL Fix...")
    ssh.connect(hostname, username=username, password=password, timeout=10)
    
    try:
        # 1. Sauvegarder la conf originale
        print("--- 1. Sauvegarde de la configuration Nginx ---")
        ssh.exec_command("cp /app/nginx/default.conf /app/nginx/default.conf.ssl_backup")
        
        # 2. Remplacer par une configuration temporaire HTTP-only (pour valider Let's Encrypt sans crash)
        minimal_nginx = """
server {
    listen 80;
    server_name logertogo.com www.logertogo.com agence.logertogo.com hotels.logertogo.com finance.digitalh.net agence.logersenegal.com digitalh.net www.digitalh.net save.digitalh.net doro.digitalh.net influenceur.digitalh.net pari.digitalh.net www.pari.digitalh.net;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 'Renouvellement SSL en cours... Veuillez patienter 1 minute.';
        add_header Content-Type text/plain;
    }
}
"""
        sftp = ssh.open_sftp()
        with sftp.file('/app/nginx/default.conf', 'w') as f:
            f.write(minimal_nginx)
        sftp.close()
        
        # 3. Démarrer Nginx avec cette config minimaliste
        print("--- 2. Démarrage de Nginx en mode HTTP-only ---")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart nginx", get_pty=True)
        for line in stdout: sys.stdout.write(line)
            
        # Nettoyage des dossiers certbot au cas où
        ssh.exec_command("rm -Rf /app/certbot/conf/live/* /app/certbot/conf/archive/* /app/certbot/conf/renewal/*")
            
        # 4. Demander les certificats
        cert_commands = [
            "docker compose run --rm --entrypoint \"certbot certonly --webroot -w /var/www/certbot --email contact@logertogo.com --rsa-key-size 4096 --agree-tos --force-renewal -n -d logertogo.com -d www.logertogo.com -d agence.logertogo.com -d hotels.logertogo.com\" certbot",
            "docker compose run --rm --entrypoint \"certbot certonly --webroot -w /var/www/certbot --email contact@logertogo.com --rsa-key-size 4096 --agree-tos --force-renewal -n -d finance.digitalh.net\" certbot",
            "docker compose run --rm --entrypoint \"certbot certonly --webroot -w /var/www/certbot --email contact@logertogo.com --rsa-key-size 4096 --agree-tos --force-renewal -n -d agence.logersenegal.com\" certbot",
            "docker compose run --rm --entrypoint \"certbot certonly --webroot -w /var/www/certbot --email contact@logertogo.com --rsa-key-size 4096 --agree-tos --force-renewal -n -d digitalh.net -d www.digitalh.net\" certbot",
            "docker compose run --rm --entrypoint \"certbot certonly --webroot -w /var/www/certbot --email contact@logertogo.com --rsa-key-size 4096 --agree-tos --force-renewal -n -d save.digitalh.net\" certbot",
            "docker compose run --rm --entrypoint \"certbot certonly --webroot -w /var/www/certbot --email contact@logertogo.com --rsa-key-size 4096 --agree-tos --force-renewal -n -d doro.digitalh.net\" certbot",
            "docker compose run --rm --entrypoint \"certbot certonly --webroot -w /var/www/certbot --email contact@logertogo.com --rsa-key-size 4096 --agree-tos --force-renewal -n -d influenceur.digitalh.net\" certbot",
            "docker compose run --rm --entrypoint \"certbot certonly --webroot -w /var/www/certbot --email contact@logertogo.com --rsa-key-size 4096 --agree-tos --force-renewal -n -d www.pari.digitalh.net -d pari.digitalh.net\" certbot"
        ]
        
        print("\n--- 3. Téléchargement de Let's Encrypt ---")
        for cmd in cert_commands:
            stdin, stdout, stderr = ssh.exec_command(f"cd /app && {cmd}", get_pty=True)
            for line in stdout: sys.stdout.write(line)
            
        # 5. Restaurer la configuration Nginx complète
        print("\n--- 4. Restauration de la configuration HTTPS et redémarrage final ---")
        ssh.exec_command("mv /app/nginx/default.conf.ssl_backup /app/nginx/default.conf")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart nginx", get_pty=True)
        for line in stdout: sys.stdout.write(line)
            
        print("\n✅ TOUT EST TERMINÉ ! Le site doit être en ligne.")
        
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    ultimate_ssl_fix()
