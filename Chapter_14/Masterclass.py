
class BasicModule:
    """Docstring: Defines the purpose of this component."""    
    def __init__(self, name: str, version: float):
        self.name = name  
        self.version = version 
   
    def report_status(self) -> str:        
        return f"Module {self.name} (v{self.version}) operational."
    

core_monitor = BasicModule(name="Core Sensor Array", version=2.1) 
print(core_monitor.name)        
print(core_monitor.report_status())


secondary_system = BasicModule(name="Backup Power Module", version=1.5)
print(secondary_system.name)
print(secondary_system.report_status())