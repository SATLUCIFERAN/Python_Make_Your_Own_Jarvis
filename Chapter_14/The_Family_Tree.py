

class JAVISBaseComponent:
    """PARENT Class: Holds common features ALL JAVIS components need."""
    def __init__(self, component_id: int):
        self.component_id = component_id
        self.is_active = True
        
    def get_base_status(self) -> str:
        return f"ID {self.component_id} is active: {self.is_active}."

class PowerRegulator(JAVISBaseComponent):
    """
    CHILD Class: INHERITS from JAVISBaseComponent. 
    A PowerRegulator IS-A JAVISBaseComponent.
    """
    def __init__(self, component_id: int, max_wattage: int):        
        super().__init__(component_id) 
        self.max_wattage = max_wattage 
        
    def check_load(self, current_load) -> str:       
        base_status = self.get_base_status() 
        if current_load > self.max_wattage:
            return f"{base_status} ERROR: Overload at {current_load}W!"
        return f"{base_status} Load Nominal."


regulator = PowerRegulator(component_id=205, max_wattage=5000)

print(regulator.check_load(current_load=4500))
print(regulator.check_load(current_load=6100))