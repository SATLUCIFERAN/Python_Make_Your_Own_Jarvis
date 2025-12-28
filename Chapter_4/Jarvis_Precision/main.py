
# Import only the specific function we need

from system_monitoring import check_temp

# We can now call the function directly

core_temp = check_temp("core") 
print(f"Core Temp: {core_temp}°C")

# --- Example of importing multiple items at once: ---
#from data_utilities import parse_json, clean_text