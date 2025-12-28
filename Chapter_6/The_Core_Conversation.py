
import requests


ISS_API = "http://api.open-notify.org/iss-now.json"
response = requests.get(ISS_API)

if response.status_code == 200:    
    data = response.json()
    print(data)    
    lat = data['iss_position']['latitude']
    lon = data['iss_position']['longitude']    
    print("J.A.R.V.I.S. Reports:")
    print(f"The ISS is currently located at Lat: {lat}, Lon: {lon}")

else:    
    print(f"Alert: Failed to contact ISS API. Status code: {response.status_code}")



    