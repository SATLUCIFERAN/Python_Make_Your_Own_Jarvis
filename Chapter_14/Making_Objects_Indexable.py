
class Sensor:
    """A simple sensor component."""
    def __init__(self, name: str, is_active: bool):
        self.name = name
        self.is_active = is_active

class SystemDashboard:
    """
    A coordinator that manages a collection of Sensor objects.
    Now supports bracket access [].
    """
    def __init__(self, sensors: list):
        # Store sensors as a dictionary for easy name-based lookups
        self.sensors_by_name = {s.name: s for s in sensors}
    
    def __getitem__(self, key: str | int) -> Sensor:
        """
        __getitem__: Defines behavior when dashboard[key] is called.
        Allows access by sensor name (string) or sequential index (int).
        """
        if isinstance(key, str):
            # String Key: Dictionary-style access
            if key in self.sensors_by_name:
                return self.sensors_by_name[key]
            raise KeyError(f"Sensor '{key}' not found.")
        
        elif isinstance(key, int):
            # Integer Key: List-style access
            sensor_list = list(self.sensors_by_name.values())
            if 0 <= key < len(sensor_list):
                return sensor_list[key]
            raise IndexError("Sensor index out of range.")
        
        else:
            raise TypeError("Key must be a sensor name (str) or index (int).")

# --- Usage ---

dashboard = SystemDashboard([
    Sensor("Main Arc Status", True),
    Sensor("Plasma Coil Temp", True),
    Sensor("Flight Control", True),
])

print("--- Accessing by Name (Dictionary-style) ---")
arc_sensor = dashboard["Main Arc Status"]
print(f"Sensor 1: {arc_sensor.name}")

print("\n--- Accessing by Index (List-style) ---")
temp_sensor = dashboard[1] # Gets the second sensor
print(f"Sensor 2: {temp_sensor.name}")
