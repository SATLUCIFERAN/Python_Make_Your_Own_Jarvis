
class PowerSource:
    """Component 1: Manages the charge level and status."""
    def __init__(self, charge_level: int = 100):
        self.charge_level = charge_level
    
    def get_status(self) -> str:
        return f"Arc Reactor Status: {self.charge_level}%."
    
    def drain(self, amount: int):
        self.charge_level -= amount

class TargetingSystem:
    """Component 2: Handles target acquisition logic."""
    def acquire(self, target: str) -> str:
        return f"Targeting System Active: Locked on {target}."


class IronManSuit:
    """
    The main, composite class. 
    It HAS A PowerSource and HAS A TargetingSystem.
    """
    def __init__(self):        
        self.power_source = PowerSource() 
        self.targeting_system = TargetingSystem()
        self.boot_status = "OK"
        

 # DELEGATION: The suit simply forwards the request to the component.
    def check_power(self) -> str:
        """Delegates power status check to the PowerSource component."""
        return self.power_source.get_status()
    

  # DELEGATION & COORDINATION: The suit delegates the combat action.
    def engage_target(self, target: str) -> str:
        """Delegates target acquisition and uses power."""
        if self.power_source.charge_level < 10:
            return "WARNING: Insufficient power for combat action."        
        # 1. Delegation: Power drain happens here
        self.power_source.drain(10)        
        # 2. Delegation: Targeting happens here
        lock_status = self.targeting_system.acquire(target)        
        # Return composite result
        return f"Engaging. {lock_status}. Power Remaining: {self.check_power()}"



# Usage: The developer interacts only with the composite suit object.

suit = IronManSuit()

print("--- Suit Initialization ---")
print(suit.check_power())

print("\n--- Combat Sequence ---")
print(suit.engage_target("Mandarin's Base"))
print(suit.engage_target("Drone Swarm"))
print(suit.check_power())

