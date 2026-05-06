from logersn.models import Property
from django.utils import timezone
import datetime
import random

def run():
    # Boost some properties
    props = list(Property.objects.all())
    if not props:
        print("No properties found.")
        return
        
    random.shuffle(props)
    boosted_count = 0
    for p in props[:5]:
        p.is_boosted = True
        p.boost_until = timezone.now() + datetime.timedelta(days=30)
        p.save()
        print(f"Boosted: {p.title}")
        boosted_count += 1
    
    print(f"Finished. Boosted {boosted_count} properties.")

if __name__ == "__main__":
    run()
