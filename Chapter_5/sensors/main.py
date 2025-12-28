
import csv
from pathlib import Path

sensors_path = Path("sensors")/"temp_log.csv"
core_temps = []

with open(sensors_path, mode="r", newline="") as f:    
    reader = csv.reader(f) 
    header = next(reader)       
    for row in reader:   
        print(row)
        print(row[1])    
        core_temps.append(int(row[1]))
avg_temp = sum(core_temps) / len(core_temps)

print(f"Header Keys: {header}")
print(f"Average Core Temp: {avg_temp:.2f}°C")

