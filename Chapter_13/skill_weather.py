

import requests
import json
import os 

API_KEY = os.environ.get("WEATHER_API_KEY") 

def get_current_temp(city: str) -> float:    
    base_url = "https://api.weather.com/v1"    
    response = requests.get(
        f"{base_url}/current?city={city}&apikey={API_KEY}"
    )    
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        return temp
    else:        
        return 0.0
    
# The updated content of skill_weather.py on the branch:
def format_for_speech(data: dict) -> str:   
    condition = "condition"
    phrase = f"The current temperature... and conditions are {condition}."
    return phrase
