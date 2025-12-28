

import requests

def get_secret_weather_report(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()         
        data = response.json()
        temp = data['forecast']['temp']         
        return f"Current temperature: {temp}°C"
        
    
    except requests.exceptions.HTTPError as e:        
        return f"Alert: API access failed with error {e}. Check API key or URL."        
    except KeyError:        
        return "Warning: Data structure unexpected. Cannot find temperature key."        
    except Exception as e:        
        return f"FATAL ERROR: A critical, unhandled error occurred: {e}"

print(get_secret_weather_report("http://bad-url.com/api"))


