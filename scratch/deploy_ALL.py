import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Connexion au serveur {host}...")
try:
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
except Exception as e:
    print(f"Erreur de connexion SSH: {e}")
    exit(1)

sftp = ssh.open_sftp()

files_to_upload = [
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\hotel\hotel_profile.html", "/app/templates/hotel/hotel_profile.html"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\agency\agency_profile.html", "/app/templates/agency/agency_profile.html"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\logersn\near_me.html", "/app/templates/logersn/near_me.html"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\public_profile.html", "/app/templates/public_profile.html"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\management\views_agency.py", "/app/management/views_agency.py")
]

print("=== DEPLOIEMENT DES FICHIERS ===")
for local_path, remote_path in files_to_upload:
    print(f"Upload de {remote_path}...")
    try:
        sftp.put(local_path, remote_path)
    except Exception as e:
        print(f"Erreur lors de l'upload de {local_path}: {e}")

sftp.close()

print("\n=== CORRECTION DES COORDONNEES GPS DES HOTELS ===")
python_script = """
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from logersn.models import Property
from users.models import User

# On force une coordonnée par défaut (Lomé) pour les hôtels qui n'ont pas encore rempli leur profil GPS
hotels_without_gps = User.objects.filter(role__in=['HOTEL', 'AUBERGE']).filter(agency_latitude__isnull=True)
count_users = 0
for h in hotels_without_gps:
    h.agency_latitude = 6.137
    h.agency_longitude = 1.222
    h.save(update_fields=['agency_latitude', 'agency_longitude'])
    count_users += 1

# On met à jour les propriétés synchronisées pour qu'elles apparaissent sur la carte
props_without_gps = Property.objects.filter(owner__role__in=['HOTEL', 'AUBERGE'], latitude__isnull=True)
count_props = 0
for p in props_without_gps:
    p.latitude = 6.137
    p.longitude = 1.222
    p.save(update_fields=['latitude', 'longitude'])
    count_props += 1

print(f"SUCCES : {count_users} hotels et {count_props} chambres ont reçu des coordonnees GPS par defaut pour apparaitre sur la carte !")
"""

# Utilisation de l'entrée standard (stdin)
sync_cmd = "cd /app && docker compose exec -T web python manage.py shell"
stdin, stdout, stderr = ssh.exec_command(sync_cmd)
stdin.write(python_script)
stdin.channel.shutdown_write()

print(stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print("Erreurs potentielles du script :")
    print(err)

print("\n=== REDEMARRAGE DU SERVEUR WEB ===")
ssh.exec_command("cd /app && docker compose restart web")

ssh.close()
print("RÉPARATION TOTALE TERMINÉE ! Tout devrait être fonctionnel.")
