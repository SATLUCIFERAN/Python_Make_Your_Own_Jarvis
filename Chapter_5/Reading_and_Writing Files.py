
from pathlib import Path
from datetime import datetime 


log_file = Path("jarvis.log")
time_of_day = datetime.now().strftime("%H:%M:%S")
log_data = "System check passed: All core skills online."


with open(log_file, mode="a") as f:
    f.write(f"[{time_of_day}] {log_data}\n")

with open(log_file, mode="r") as f:
    full_log = f.read()
    

print("\n--- Last 50 characters of log: ---")
print(full_log[0:50])