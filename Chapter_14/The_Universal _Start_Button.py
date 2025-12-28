

class ThermalSensor:
    """Polymorphic Form 1: Displays temperature data."""
    def display_data(self) -> str:
        return "DISPLAYING: Temperature graph (Red to Blue gradient)."

class AcousticSensor:
    """Polymorphic Form 2: Displays sound data 
       (Same method name, different action)."""
    def display_data(self) -> str:
        return "DISPLAYING: Sound wave frequency chart (Green line plot)."

class HologramProjector:
    """The system that uses Polymorphism."""
    def project(self, component):        
        print(f"Projector received data from: {component.__class__.__name__}")
        print(component.display_data())


projector = HologramProjector()
projector.project(ThermalSensor())
projector.project(AcousticSensor())

