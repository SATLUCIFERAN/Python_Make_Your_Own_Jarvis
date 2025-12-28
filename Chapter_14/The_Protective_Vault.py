
class ArcReactor:
    """Demonstrates Encapsulation by controlling temperature setting."""    
    _MAX_SAFE_TEMP = 1000
    
    def __init__(self, initial_temp: int = 500):        
        self.__temperature = initial_temp
        
   
    def get_temperature(self) -> int:
        return self.__temperature

    
    def set_temperature(self, new_temp: int) -> str:        
        if 0 <= new_temp <= self._MAX_SAFE_TEMP:
            self.__temperature = new_temp
            return f"Temperature set to {new_temp}°C. Status: Nominal."
        else:
            return f"WARNING: {new_temp}°C is outside the safe range (0-{self._MAX_SAFE_TEMP}°C). Change denied."


reactor = ArcReactor()


# Attempting to access Private data directly (Unauthorized Access)
print(reactor.__temperature) # <-- This will cause an error!

# Reading the temperature using the controlled method (Allowed)
print(f"Initial Temp: {reactor.get_temperature()}°C")

# Using the controlled, Encapsulated method (The correct way - SUCCESS)
print(reactor.set_temperature(new_temp=900))
print(f"New Temp (Success): {reactor.get_temperature()}°C")

# Using the controlled, Encapsulated method (The correct way - FAILURE)

print(reactor.set_temperature(new_temp=1500))
print(f"New Temp (Failure): {reactor.get_temperature()}°C")
