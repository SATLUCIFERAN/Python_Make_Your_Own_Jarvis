
import random

class JAVISLogEntry:
    # ... __init__ and __str__ are here ...
    def __init__(self, component_name: str, status: str, level: int):
        self.component_name = component_name
        self.status = status
        self.level = level
        self.timestamp = random.randint(1000000, 9999999) 

    def __str__(self) -> str:
        return f"[LOG-{self.timestamp}] {self.component_name}: {self.status} (L{self.level})"

    def __repr__(self) -> str:
        """
        __repr__: Debugging output (what the developer sees).
        This format shows the class and its essential parameters.
        """
        return f"JAVISLogEntry(component_name='{self.component_name}', status='{self.status}', level={self.level})"

# --- Usage ---
entry = JAVISLogEntry("Arc_Reactor_A", "Thermal Warning", 3)

# 2. Triggering __repr__ (for developer inspection)
# The repr() function explicitly calls this method:
print(f"Developer Debug: {repr(entry)}")
