
import random

class JAVISLogEntry:   
    def __init__(self, component_name: str, status: str, level: int):
        self.component_name = component_name
        self.status = status
        self.level = level        
        self.timestamp = random.randint(1000000, 9999999) 


entry = JAVISLogEntry("Arc_Reactor_A", "Thermal Warning", 3)

print(entry)
