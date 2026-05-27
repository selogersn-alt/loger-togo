import paramiko

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)

script = '''
import sys
sys.path.insert(0, '/app')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
import django
django.setup()

from django.test import RequestFactory
from users.models import User
from management.models import HotelBooking
import traceback

print("Diagnostic script starting...")

try:
    booking = HotelBooking.objects.latest('created_at')
    hotel = booking.room.hotel
    print(f"Testing with booking {booking.id} for hotel {hotel}")
    
    from management.views_hotel import hotel_booking_detail
    rf = RequestFactory()
    request = rf.get(f'/reservations/{booking.id}/', HTTP_HOST='hotels.logertogo.com')
    request.user = hotel
    request.urlconf = 'logertogo.urls_hotel'
    
    try:
        response = hotel_booking_detail(request, booking_id=booking.id)
        if response.status_code == 200:
            print("OK - The view rendered successfully when simulated.")
        else:
            print(f"Status Code: {response.status_code}")
    except Exception as e:
        print(f"VIEW CRASHED! Type: {type(e).__name__}, Msg: {e}")
        traceback.print_exc()

except Exception as e:
    print(f"Setup Error: {e}")
'''

# Save the script to the host
sftp = ssh.open_sftp()
with sftp.file('/root/diag_now.py', 'w') as f:
    f.write(script)
sftp.close()

# Pass the script into the docker container via standard input
stdin, stdout, stderr = ssh.exec_command("cat /root/diag_now.py | docker compose -f /app/docker-compose.yml exec -T web python")
out = stdout.read().decode('utf-8', 'replace')
err = stderr.read().decode('utf-8', 'replace')

with open("scratch/diag_result.txt", "w", encoding="utf-8") as f:
    f.write("=== STDOUT ===\n" + out + "\n=== STDERR ===\n" + err)

print("DIAGNOSTIC SAVED.")
ssh.close()
