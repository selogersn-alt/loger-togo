import paramiko, sys

host = "157.180.127.70"
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username='root', password='AkueMax@2022', timeout=30)

# The 500 error is still happening - Gunicorn logs don't show Django traceback by default.
# Let's get it directly by triggering the view and capturing the exception.
script = '''
import sys
sys.path.insert(0, '/app')
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
import django
django.setup()

from django.test import RequestFactory, Client
from users.models import User
from management.models import HotelBooking
import traceback

# Use the booking UUID from the logs
booking_ids = ['1a1a9345-1230-47b6-b646-3fffe6e05a8f', '3817dbe4-bd5a-4c90-adde-d071c9ae4f2a']

for bid in booking_ids:
    try:
        b = HotelBooking.objects.get(id=bid)
        hotel = b.room.hotel
        print(f"Testing booking {bid[:8]}... Hotel: {hotel}")
        
        # Simulate the actual view call
        from management.views_hotel import hotel_booking_detail
        rf = RequestFactory()
        request = rf.get(f'/reservations/{bid}/', HTTP_HOST='hotels.logertogo.com')
        request.user = hotel
        request.urlconf = 'logertogo.urls_hotel'
        
        try:
            response = hotel_booking_detail(request, booking_id=b.id)
            print(f"  Response status: {response.status_code}")
            if response.status_code == 200:
                print("  OK - Page renders correctly!")
            else:
                print(f"  Response content: {response.content[:500]}")
        except Exception as e:
            print(f"  VIEW ERROR: {type(e).__name__}: {e}")
            traceback.print_exc()
    except HotelBooking.DoesNotExist:
        print(f"Booking {bid} not found")
    except Exception as e:
        print(f"Error for {bid}: {type(e).__name__}: {e}")
        traceback.print_exc()
'''

with open('/tmp/full_diag.py', 'w') as f:
    f.write(script)

sftp = ssh.open_sftp()
sftp.put('/tmp/full_diag.py', '/tmp/full_diag.py')
sftp.close()

# Actually write it directly
import paramiko
sftp = ssh.open_sftp()
with sftp.file('/tmp/full_diag.py', 'w') as f:
    f.write(script)
sftp.close()

cmd = "cd /app && docker compose exec -T web python /tmp/full_diag.py"
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
stdout.channel.recv_exit_status()
out = stdout.read()
err = stderr.read()

with open('scratch/full_diag_output.txt', 'wb') as f:
    f.write(b"=== STDOUT ===\n")
    f.write(out)
    f.write(b"\n=== STDERR ===\n")
    f.write(err)

print("Output saved to scratch/full_diag_output.txt")
print("STDOUT preview:", out[:2000].decode('utf-8', 'replace'))
if err:
    print("STDERR preview:", err[:2000].decode('utf-8', 'replace'))

ssh.close()
