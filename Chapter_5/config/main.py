
import json
from pathlib import Path

config_path = Path("config") / "status.json"
with open(config_path, mode="r") as f:   
    status_dict = json.load(f) 
    
print(f"Status is: {status_dict['status']}")
print(f"Users found: {len(status_dict['active_users'])}")


status_dict['status'] = "maintenance"
status_dict['last_check'] = 1678886500

with open(config_path, mode="w") as f:   
    json.dump(status_dict, f, indent=4)