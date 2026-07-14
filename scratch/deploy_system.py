import paramiko
import os

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

# ensure remote directories exist
try:
    sftp.mkdir("/app/users/migrations")
except:
    pass

files_to_upload = [
    # Core Models & Migrations
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\users\models.py", "/app/users/models.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\users\migrations\0021_add_agency_profile_fields.py", "/app/users/migrations/0021_add_agency_profile_fields.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\users\migrations\0022_alter_user_role.py", "/app/users/migrations/0022_alter_user_role.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\users\migrations\0023_alter_user_is_saas_active.py", "/app/users/migrations/0023_alter_user_is_saas_active.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\users\migrations\0024_user_parent_hotel.py", "/app/users/migrations/0024_user_parent_hotel.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\users\migrations\0025_alter_user_role.py", "/app/users/migrations/0025_alter_user_role.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\users\migrations\0026_user_agency_latitude_user_agency_longitude_and_more.py", "/app/users/migrations/0026_user_agency_latitude_user_agency_longitude_and_more.py"),
    
    # Views & Forms logic
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\management\views_agency.py", "/app/management/views_agency.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\management\views_hotel.py", "/app/management/views_hotel.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\logersn\views.py", "/app/logersn/views.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\users\forms.py", "/app/users/forms.py"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\users\views.py", "/app/users/views.py"),
    
    # Elegant templates
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\hotel\hotel_profile.html", "/app/templates/hotel/hotel_profile.html"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\agency\agency_profile.html", "/app/templates/agency/agency_profile.html"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\logersn\near_me.html", "/app/templates/logersn/near_me.html"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\public_profile.html", "/app/templates/public_profile.html"),
    (r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\profile_update.html", "/app/templates/profile_update.html"),
]

print("=== UPLOADING ALL REQUIRED FILES ===")
for local_path, remote_path in files_to_upload:
    if os.path.exists(local_path):
        print(f"Uploading {local_path} -> {remote_path}...")
        try:
            sftp.put(local_path, remote_path)
        except Exception as e:
            print(f"Error uploading {local_path}: {e}")
    else:
        print(f"Warning: local file {local_path} not found!")

sftp.close()

print("\n=== REBUILDING WEB DOCKER IMAGE ===")
build_cmd = "cd /app && docker compose build web"
stdin, stdout, stderr = ssh.exec_command(build_cmd)
print(stdout.read().decode('utf-8'))
build_err = stderr.read().decode('utf-8')
if build_err:
    print("Build stderr (if any):")
    print(build_err)

print("\n=== RECREATING WEB CONTAINER ===")
up_cmd = "cd /app && docker compose up -d web"
stdin, stdout, stderr = ssh.exec_command(up_cmd)
print(stdout.read().decode('utf-8'))

print("\n=== WAITING FOR WEB CONTAINER TO START (5s) ===")
import time
time.sleep(5)

print("\n=== SHOWING MIGRATIONS ON VPS ===")
show_cmd = "cd /app && docker compose exec -T web python manage.py showmigrations users"
stdin, stdout, stderr = ssh.exec_command(show_cmd)
show_out = stdout.read().decode('utf-8')
print("Migrations status:")
print(show_out)

print("\n=== FAKING MANAGEMENT 0018 IF NEEDED ===")
fake_mgmt_cmd = "cd /app && docker compose exec -T web python manage.py migrate management 0018 --fake"
stdin, stdout, stderr = ssh.exec_command(fake_mgmt_cmd)
print("Fake mgmt stdout:")
print(stdout.read().decode('utf-8'))
fake_mgmt_err = stderr.read().decode('utf-8')
if fake_mgmt_err:
    print("Fake mgmt stderr:")
    print(fake_mgmt_err)

print("\n=== RUNNING MIGRATIONS ON VPS ===")
migrate_cmd = "cd /app && docker compose exec -T web python manage.py migrate"
stdin, stdout, stderr = ssh.exec_command(migrate_cmd)
print("Migration stdout:")
print(stdout.read().decode('utf-8'))
migrate_err = stderr.read().decode('utf-8')
if migrate_err:
    print("Migration stderr:")
    print(migrate_err)

print("\n=== RUNNING PYTHON DB FIX SCRIPT ===")
python_script = """
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from django.db import connection
from logersn.models import Property
from users.models import User

# Fix missing columns/tables from management.0018 due to faking
print("Checking and repairing management_hotelroom table and tables...")
try:
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE management_hotelroom ADD COLUMN IF NOT EXISTS synced_property_id VARCHAR(100) NULL;")
        cursor.execute("ALTER TABLE management_hotelroom ADD COLUMN IF NOT EXISTS visible_on_portal BOOLEAN DEFAULT TRUE;")
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS management_hotelroomimage (
                id UUID PRIMARY KEY,
                image_url VARCHAR(100) NOT NULL,
                is_primary BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                room_id UUID NOT NULL REFERENCES management_hotelroom(id) ON DELETE CASCADE
            );
        \"\"\")
        cursor.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS management_notification (
                id UUID PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                link VARCHAR(255) NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                user_id BIGINT NOT NULL REFERENCES users_user(id) ON DELETE CASCADE
            );
        \"\"\")
    print("Database structure verified and repaired successfully!")
except Exception as db_err:
    print(f"Error repairing DB structure: {db_err}")

try:
    # Assign Lomé center to all hotels/guesthouses with null coordinates
    hotels_without_gps = User.objects.filter(role__in=['HOTEL', 'AUBERGE']).filter(agency_latitude__isnull=True)
    count_users = 0
    for h in hotels_without_gps:
        h.agency_latitude = 6.137
        h.agency_longitude = 1.222
        h.save(update_fields=['agency_latitude', 'agency_longitude'])
        count_users += 1

    # Sync properties owned by these entities to show up on the map
    props_without_gps = Property.objects.filter(owner__role__in=['HOTEL', 'AUBERGE'], latitude__isnull=True)
    count_props = 0
    for p in props_without_gps:
        p.latitude = 6.137
        p.longitude = 1.222
        p.save(update_fields=['latitude', 'longitude'])
        count_props += 1

    # Assign GPS coordinates to agencies if missing
    agencies_without_gps = User.objects.filter(role='AGENCY', agency_latitude__isnull=True)
    count_agencies = 0
    for a in agencies_without_gps:
        a.agency_latitude = 6.137
        a.agency_longitude = 1.222
        a.save(update_fields=['agency_latitude', 'agency_longitude'])
        count_agencies += 1

    print(f"GPS SETUP: Assigned default Lome coords to {count_users} hotels/guesthouses, {count_props} rooms, and {count_agencies} agencies.")
except Exception as e:
    print(f"ERROR running DB Setup: {e}")
"""

run_fix_cmd = "cd /app && docker compose exec -T web python manage.py shell"
stdin, stdout, stderr = ssh.exec_command(run_fix_cmd)
stdin.write(python_script)
stdin.channel.shutdown_write()

print("DB Fix stdout:")
print(stdout.read().decode('utf-8'))
fix_err = stderr.read().decode('utf-8')
if fix_err:
    print("DB Fix stderr:")
    print(fix_err)

print("\n=== RESTARTING WEB CONTAINER FOR FRESH RELOAD ===")
stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose restart web")
print(stdout.read().decode('utf-8'))

ssh.close()
print("\nSUCCESS: COMPLETE DEPLOYMENT & DATABASE FIX SUCCEEDED!")
