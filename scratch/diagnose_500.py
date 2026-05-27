import paramiko
import sys

host = "157.180.127.70"
port = 22
username = "root"
password = "AkueMax@2022"

print(f"Connexion au serveur {host}...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(host, port=port, username=username, password=password, timeout=30)
    print("Connecte!\n")

    # Get the Django debug traceback - we need DEBUG=True temporarily or error logs
    # First let's try to get the actual Django traceback from a 500 request
    cmd = "cd /app && docker compose exec -T web python -c \"\
import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE','logertogo.settings'); django.setup();\
from django.test import RequestFactory;\
from management.models import HotelBooking;\
b = HotelBooking.objects.first();\
print('Booking found:', b);\
print('total_amount:', b.total_amount if b else 'N/A');\
print('balance_due:', b.balance_due if b else 'N/A');\
print('unique_ref:', b.unique_ref if b else 'N/A');\
if b:\
  for c in b.charges.all():\
    print('charge total_price:', c.total_price);\
print('ALL OK');\
\""

    print("Test des proprietes HotelBooking en production...")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    print("STDOUT:", out)
    if err:
        print("STDERR:", err)

    print("\n" + "="*60)

    # Also check the template rendering error via the actual view
    cmd2 = "cd /app && docker compose exec -T web python manage.py shell -c \"\
from management.models import HotelBooking, HotelChargeItem;\
import builtins;\
b = HotelBooking.objects.first();\
if b:\
  print('Booking:', b);\
  print('total_amount type:', type(b.total_amount));\
  print('balance_due type:', type(b.balance_due));\
  print('unique_ref:', b.unique_ref);\
  charges = b.charges.all();\
  for c in charges:\
    print('HotelChargeItem total_price:', c.total_price);\
  print('OK - no errors');\
else:\
  print('No bookings found');\
\""

    print("Django shell test...")
    stdin2, stdout2, stderr2 = ssh.exec_command(cmd2, timeout=60)
    stdout2.channel.recv_exit_status()
    out2 = stdout2.read().decode('utf-8', errors='replace').strip()
    err2 = stderr2.read().decode('utf-8', errors='replace').strip()
    print("STDOUT:", out2)
    if err2:
        print("STDERR:", err2)

    # Get the actual error traceback from the view
    print("\n" + "="*60)
    cmd3 = "cd /app && docker compose exec -T web python manage.py shell -c \"\
from django.test import RequestFactory, Client;\
from users.models import User;\
hotel = User.objects.filter(role='HOTEL').first();\
print('Hotel user:', hotel);\
from management.models import HotelBooking;\
b = HotelBooking.objects.filter(room__hotel=hotel).first() if hotel else None;\
print('Booking:', b);\
if b:\
  from django.template.loader import render_to_string;\
  from django.test import RequestFactory;\
  rf = RequestFactory();\
  request = rf.get('/reservations/{}/'.format(b.id), HTTP_HOST='hotels.logertogo.com');\
  request.user = hotel;\
  try:\
    content = render_to_string('hotel/hotel_booking_detail.html', {'booking': b, 'charges': b.charges.all()}, request=request);\
    print('Template OK - length:', len(content));\
  except Exception as e:\
    print('TEMPLATE ERROR:', type(e).__name__, str(e));\
    import traceback; traceback.print_exc();\
\""
    print("Test rendu du template hotel_booking_detail...")
    stdin3, stdout3, stderr3 = ssh.exec_command(cmd3, timeout=60)
    stdout3.channel.recv_exit_status()
    out3 = stdout3.read().decode('utf-8', errors='replace').strip()
    err3 = stderr3.read().decode('utf-8', errors='replace').strip()
    print("STDOUT:", out3)
    if err3:
        print("STDERR:", err3)

except Exception as e:
    print(f"Erreur: {e}")
    sys.exit(1)
finally:
    ssh.close()
