import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Connexion au serveur {host}...")
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)

print("Synchronisation des anciennes chambres d'hôtel vers le portail public...")
python_script = """
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from management.models import HotelRoom

rooms = HotelRoom.objects.all()
count = 0
for room in rooms:
    room.save()
    count += 1

print(f"SUCCES : {count} chambres d'hotel ont ete synchronisees vers logertogo.com !")
"""

# Utilisation de l'entrée standard (stdin) pour éviter les erreurs de guillemets dans Bash
sync_cmd = "cd /app && docker compose exec -T web python manage.py shell"
stdin, stdout, stderr = ssh.exec_command(sync_cmd)

# Injection du script Python
stdin.write(python_script)
stdin.channel.shutdown_write()

print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
print("Terminé !")
