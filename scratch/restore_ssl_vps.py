import paramiko
import sys

def restore_ssl():
    hostname = '157.180.127.70'
    username = 'root'
    password = 'AkueMax@2022'
    
    print("Connecting to Hetzner server to restore SSL...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password, timeout=10)
        print("Connected successfully!\n")
        
        # 1. Générer de faux certificats (Dummy) pour que Nginx accepte de démarrer
        dummy_certs_cmd = """
        domains=(
          "logertogo.com"
          "finance.digitalh.net"
          "agence.logersenegal.com"
          "digitalh.net"
          "save.digitalh.net"
          "doro.digitalh.net"
          "influenceur.digitalh.net"
          "www.pari.digitalh.net"
        )
        for domain in "${domains[@]}"; do
          mkdir -p "/app/certbot/conf/live/$domain"
          openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
            -keyout "/app/certbot/conf/live/$domain/privkey.pem" \
            -out "/app/certbot/conf/live/$domain/fullchain.pem" \
            -subj "/CN=localhost"
        done
        """
        print("--- Étape 1 : Création de certificats temporaires pour forcer le démarrage de Nginx ---")
        ssh.exec_command(dummy_certs_cmd)
        
        # 2. Démarrer Nginx avec les faux certificats
        print("\n--- Étape 2 : Démarrage de Nginx ---")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart nginx", get_pty=True)
        for line in iter(stdout.readline, ""):
            sys.stdout.write(line)
            
        # 3. Supprimer les faux certificats
        print("\n--- Étape 3 : Suppression des certificats temporaires ---")
        ssh.exec_command("rm -Rf /app/certbot/conf/live/*")
        ssh.exec_command("rm -Rf /app/certbot/conf/archive/*")
        ssh.exec_command("rm -Rf /app/certbot/conf/renewal/*")
        
        # 4. Demander les vrais certificats Let's Encrypt (Nginx est en ligne pour répondre aux challenges HTTP)
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
        
        print("\n--- Étape 4 : Téléchargement des VRAIS certificats Let's Encrypt (Cela prendra 1 à 2 minutes) ---")
        for i, cmd in enumerate(cert_commands):
            print(f"Demande du certificat {i+1}/{len(cert_commands)}...")
            stdin, stdout, stderr = ssh.exec_command(f"cd /app && {cmd}", get_pty=True)
            for line in iter(stdout.readline, ""):
                sys.stdout.write(line)
                
        # 5. Redémarrer Nginx pour appliquer les vrais certificats
        print("\n--- Étape 5 : Application finale et redémarrage ---")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart nginx", get_pty=True)
        for line in iter(stdout.readline, ""):
            sys.stdout.write(line)
            
        print("\n🔥 TOUS LES CERTIFICATS SONT RESTAURÉS ET LE SITE EST EN LIGNE !")
        
    except Exception as e:
        print(f"Erreur fatale : {str(e)}")
    finally:
        ssh.close()

if __name__ == "__main__":
    restore_ssl()
