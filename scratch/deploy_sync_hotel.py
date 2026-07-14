import os
import subprocess

# Couleurs pour l'affichage
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'
CYAN = '\033[96m'

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"{GREEN}{result.stdout}{RESET}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{RED}Erreur d'exécution de la commande : {cmd}{RESET}")
        print(f"{RED}{e.stderr}{RESET}")
        return False

print(f"{CYAN}--- DEPLOIEMENT DE LA SYNCHRONISATION HOTEL-PORTAIL ---{RESET}")

print(f"{CYAN}1. Création des fichiers de migration...{RESET}")
run_command("python manage.py makemigrations users management")

print(f"{CYAN}2. Application des migrations en local...{RESET}")
run_command("python manage.py migrate")

print(f"{CYAN}3. Redémarrage du serveur de développement local (Optionnel)...{RESET}")
print(f"{GREEN}Les modifications ont été intégrées avec succès.{RESET}")
print(f"{GREEN}Si vous testez en ligne sur logertogo.com, n'oubliez pas d'exécuter votre script de déploiement distant pour appliquer ces changements et migrations !{RESET}")
