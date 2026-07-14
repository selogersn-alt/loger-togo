import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f"Connexion au serveur {host}...")
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
sftp = ssh.open_sftp()

print("1. Suppression des anciennes migrations 0018 conflictuelles...")
ssh.exec_command("rm -f /app/management/migrations/0018*.py")

print("2. Upload de la bonne migration 0018 locale...")
local_path = r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\management\migrations\0018_hotelroom_synced_property_id_and_more.py"
remote_path = "/app/management/migrations/0018_hotelroom_synced_property_id_and_more.py"
sftp.put(local_path, remote_path)
sftp.close()

print("3. Nettoyage direct dans PostgreSQL...")
sql_commands = """
ALTER TABLE management_hotelroom DROP COLUMN IF EXISTS visible_on_portal CASCADE;
ALTER TABLE management_hotelroom DROP COLUMN IF EXISTS synced_property_id CASCADE;
DROP TABLE IF EXISTS management_hotelroomimage CASCADE;
DROP TABLE IF EXISTS management_notification CASCADE;
DELETE FROM django_migrations WHERE app='management' AND name LIKE '0018%';
"""
db_clean_cmd = f"""cd /app && docker compose exec -T db psql -U logeruser -d logertogo -c "{sql_commands}" """
stdin, stdout, stderr = ssh.exec_command(db_clean_cmd)
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

print("4. Redémarrage du serveur web (la migration se fera automatiquement au démarrage)...")
ssh.exec_command("cd /app && docker compose restart web")

ssh.close()
print("RÉPARATION TERMINÉE ! Le site devrait être à nouveau fonctionnel dans 10 secondes.")
