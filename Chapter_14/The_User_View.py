
import random

class JAVISLogEntry:
    # ... __init__ is here ...
    def __init__(self, component_name: str, status: str, level: int):
        self.component_name = component_name
        self.status = status
        self.level = level
        self.timestamp = random.randint(1000000, 9999999) 

    def __str__(self) -> str:
        """
        __str__: Human-readable output (what the user sees).
        This format is optimized for concise log monitoring.
        """
        return f"[LOG-{self.timestamp}] {self.component_name}: {self.status} (L{self.level})"

# --- Usage ---
entry = JAVISLogEntry("Arc_Reactor_A", "Thermal Warning", 3)

# 1. Triggering __str__ (for user output)
print(entry) 
