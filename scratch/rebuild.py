import subprocess

print("Rebuilding Docker web container...")
result = subprocess.run(["docker", "compose", "up", "-d", "--build", "web"], capture_output=True, text=True)

if result.stdout:
    print("STDOUT:")
    print(result.stdout)
    
if result.stderr:
    print("STDERR:")
    print(result.stderr)

print(f"Return code: {result.returncode}")
if result.returncode == 0:
    print("Rebuild successful!")
else:
    print("Rebuild failed.")
