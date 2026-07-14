import os
import django
import sys

# Configure Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "logertogo.settings")
django.setup()

from logersn.models import Property

def check_visibility():
    properties = Property.objects.all().order_by('-created_at')[:10]
    print(f"Total properties: {Property.objects.count()}")
    print("\n--- Last 10 Properties ---")
    for p in properties:
        print(f"[{p.id}] {p.title}")
        print(f"  Owner: {p.owner.email} ({p.owner.role})")
        print(f"  is_published: {p.is_published}")
        print(f"  visible_on_portal: {p.visible_on_portal}")
        print(f"  is_authorized_by_admin: {p.is_authorized_by_admin}")
        print(f"  publication_requested: {p.publication_requested}")
        print("-" * 30)

if __name__ == "__main__":
    check_visibility()
