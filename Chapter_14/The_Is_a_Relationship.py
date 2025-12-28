
class BaseComponent:
    """Parent: Defines core, common behavior."""
    def get_id(self) -> str:
        return "ID: 42"

class PowerRegulator(BaseComponent): 
    """Child: Inherits BaseComponent's logic."""
    def check_status(self) -> str:        
        return f"Regulator active. Base status: {self.get_id()}" 

regulator = PowerRegulator()
print(regulator.check_status())
