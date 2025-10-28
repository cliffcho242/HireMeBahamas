import os

import psutil

# Find and kill backend processes
for proc in psutil.process_iter(["pid", "name", "cmdline"]):
    try:
        if proc.info["name"] and "python" in proc.info["name"].lower():
            cmdline = proc.info["cmdline"]
            if cmdline and any("final_backend.py" in arg for arg in cmdline):
                print(f'Killing process {proc.info["pid"]}: {" ".join(cmdline)}')
                proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

print("Backend processes killed. Starting fresh...")
