import os

req_path = r"d:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\requirements.txt"

# Read raw bytes
with open(req_path, 'rb') as f:
    raw = f.read()

# Try to decode, ignoring errors
decoded = raw.decode('utf-16le', errors='replace')

# Clean up any weird characters and lines
lines = decoded.splitlines()
clean_lines = []
for line in lines:
    line = line.strip().replace('\x00', '') # Remove null bytes
    if line and not line.startswith(''): # Skip completely corrupted lines
        clean_lines.append(line)

# Specifically ensure django-ckeditor is there
if 'django-ckeditor' not in clean_lines:
    clean_lines.append('django-ckeditor')
if 'Pillow' not in clean_lines:
    clean_lines.append('Pillow')

# Write back as proper UTF-8
with open(req_path, 'w', encoding='utf-8') as f:
    for line in clean_lines:
        f.write(line + '\n')
        
print("requirements.txt fixed and converted to UTF-8")
