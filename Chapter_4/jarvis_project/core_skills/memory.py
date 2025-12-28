
# Functions to store and retrieve data

cache = {"weather_cache": "Sunny, 25°C"}

def recall(key: str):
    return cache.get(key, "Data not found")
    
def forget(key: str):
    if key in cache:
        del cache[key]
        return True
    return False