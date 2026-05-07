import io
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from logersn.models import PropertyImage
from PIL import Image

class Command(BaseCommand):
    help = 'Convert existing property images to WebP format for high performance'

    def handle(self, *args, **options):
        images = PropertyImage.objects.all()
        total = images.count()
        self.stdout.write(f"Starting conversion of {total} images...")
        
        count = 0
        for img_obj in images:
            if not img_obj.image_url:
                continue
                
            file_path = img_obj.image_url.name
            if file_path.lower().endswith('.webp'):
                continue
                
            try:
                # Open original image
                with img_obj.image_url.open('rb') as f:
                    img = Image.open(f)
                    
                    # Convert to WebP
                    output = io.BytesIO()
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    img.save(output, format='WEBP', quality=80)
                    output.seek(0)
                    
                    # New name
                    new_name = file_path.rsplit('.', 1)[0] + '.webp'
                    
                    # Update object
                    img_obj.image_url.save(new_name, ContentFile(output.read()), save=True)
                    count += 1
                    if count % 10 == 0:
                        self.stdout.write(f"Converted {count}/{total} images...")
                        
            except Exception as e:
                self.stderr.write(f"Error converting {file_path}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Successfully converted {count} images to WebP."))
