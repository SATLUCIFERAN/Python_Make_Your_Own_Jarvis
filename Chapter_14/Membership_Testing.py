
class Sensor:
    """A simple sensor component."""
    def __init__(self, name: str, is_active: bool):
        self.name = name
        self.is_active = is_active

class SystemDashboard:
    
    def __init__(self, sensors: list):
        # Store sensor names in a set for fast lookup
        self.monitored_names = {s.name for s in sensors}

    def __contains__(self, item: str) -> bool:       
        return item in self.monitored_names

# --- Usage ---
dashboard = SystemDashboard([
    Sensor("Main Arc Status", True),
    Sensor("Plasma Coil Temp", True),
])

print("--- Membership Testing using 'in' ---")
print(f"Is 'Plasma Coil Temp' being monitored? {'Plasma Coil Temp' in dashboard}") 
print(f"Is 'Backup Battery' being monitored? {'Backup Battery' in dashboard}")



