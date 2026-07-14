import paramiko
import sys

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)
except Exception as e:
    print(f"Failed to connect: {e}")
    sys.exit(1)

check_cmd = """cd /app && docker compose run --rm web python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
tables = connection.introspection.table_names()
print('--- TABLES ---')
print('management_hotelroomimage exists:', 'management_hotelroomimage' in tables)
print('management_notification exists:', 'management_notification' in tables)

if 'management_hotelroom' in tables:
    desc = connection.introspection.get_table_description(cursor, 'management_hotelroom')
    columns = [row.name for row in desc]
    print('--- COLUMNS IN management_hotelroom ---')
    print('visible_on_portal exists:', 'visible_on_portal' in columns)
    print('synced_property_id exists:', 'synced_property_id' in columns)
" """

print("Checking remote database state...")
stdin, stdout, stderr = ssh.exec_command(check_cmd)
out = stdout.read().decode('utf-8')
err = stderr.read().decode('utf-8')

print("STDOUT:")
print(out)
print("STDERR:")
print(err)

ssh.close()
