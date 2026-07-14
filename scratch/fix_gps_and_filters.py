import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Connexion au serveur {host}...")
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)

print("Forçage des coordonnées GPS par défaut pour les hôtels...")
python_script = """
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from logersn.models import Property
from management.models import User

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

print(f"SUCCES : {count_users} hôtels et {count_props} chambres ont reçu des coordonnées GPS par défaut pour apparaître sur la carte !")
"""

# Utilisation de l'entrée standard (stdin)
sync_cmd = "cd /app && docker compose exec -T web python manage.py shell"
stdin, stdout, stderr = ssh.exec_command(sync_cmd)
stdin.write(python_script)
stdin.channel.shutdown_write()

print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

# Mettre à jour near_me.html sur le serveur
print("Mise à jour de near_me.html avec le filtre Meublé et la correction des Hôtels...")
sftp = ssh.open_sftp()
local_path = r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\logersn\near_me.html"
remote_path = "/app/templates/logersn/near_me.html"
sftp.put(local_path, remote_path)
sftp.close()

ssh.close()
print("Terminé ! Rechargez la page Autour de moi.")
