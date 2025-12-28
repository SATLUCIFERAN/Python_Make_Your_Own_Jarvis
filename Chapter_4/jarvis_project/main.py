
# 1. Importing the entire 'voice' module from the 'core_skills' package

import core_skills.voice
from core_skills.memory import recall, forget

# --- Execution ---

# Call function from the imported module using the full path

command = core_skills.voice.listen(5)
data_point = recall("weather_cache")
forget("weather_cache")

print(f"J.A.R.V.I.S. received: {command}")
print(f"Retrieved data: {data_point}")


print("Cache cleaned successfully.")