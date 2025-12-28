
# We 'import' the functions we need from the other file (module)

import system_monitoring 

core_temp = system_monitoring.check_temp("core") 
outside_temp = system_monitoring.check_temp("perimeter")

print(f"Core Temp: {core_temp}°C")
print(f"Outside Temp: {outside_temp}°C")





