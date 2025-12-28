

def calculate_power_output(core_temp: int, load_factor: float) -> float:    
    if core_temp > 90:
        return 0.0 
    return core_temp * load_factor



