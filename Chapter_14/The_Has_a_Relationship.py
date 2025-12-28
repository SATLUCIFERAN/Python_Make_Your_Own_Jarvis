
class PowerSource:
    """Component that tracks energy."""
    def __init__(self, charge_level: int = 100):
        self.charge_level = charge_level

class TargetingSystem:
    """Component that knows how to aim at a target."""
    def __init__(self, model: str = "MkVII Targeting Array"):
        self.model = model

class IronManSuit:
    """
    The suit HAS A PowerSource and HAS A TargetingSystem.
    This is composition.
    """
    def __init__(self):
        self.power_source = PowerSource(charge_level=100)
        self.targeting_system = TargetingSystem(model="MkVII Targeting Array")
        self.boot_status = "OK"


suit = IronManSuit()
print(suit.power_source.charge_level)    
print(suit.targeting_system.model)       
print(suit.boot_status)                 
