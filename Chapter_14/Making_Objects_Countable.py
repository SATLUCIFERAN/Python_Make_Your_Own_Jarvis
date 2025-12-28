
class Sensor:
    """A simple sensor component."""
    def __init__(self, name: str, is_active: bool):
        self.name = name
        self.is_active = is_active

class SystemDashboard:
    """
    A coordinator that manages a collection of Sensor objects.
    We want to be able to use len() on the dashboard.
    """
    def __init__(self, sensors: list):
        # The dashboard HAS A list of sensors (Composition)
        self.active_sensors = sensors

    def __len__(self) -> int:
        """
        __len__: Defines the behavior when len(dashboard) is called.
        We custom-define the 'length' as the count of active sensors.
        """
        return sum(1 for sensor in self.active_sensors if sensor.is_active)

# --- Usage ---

dashboard = SystemDashboard([
    Sensor("Main Arc Status", True),
    Sensor("Plasma Coil Temp", True),
    Sensor("Gravity Stabilizer", False), # Inactive
    Sensor("Flight Control", True),
])

print("--- Using len() on a Custom Object ---")
print(f"Total active components (using len()): {len(dashboard)}")
