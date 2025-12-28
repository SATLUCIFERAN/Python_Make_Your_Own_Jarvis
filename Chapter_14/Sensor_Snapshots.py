
from dataclasses import dataclass
import time

@dataclass(frozen=True) 
class SensorReading:
    """A clean, auto-built data container."""
    sensor_id: str
    value: float
    unit: str
    timestamp: float = time.time() 

# --- Usage ---
# Initialization is simple, thanks to auto-generated __init__

reading_one = SensorReading("T-404", 98.6, "C")
reading_two = SensorReading("T-404", 98.6, "C", reading_one.timestamp)
print(reading_one)
print(f"Readings are equal? {reading_one == reading_two}") 
