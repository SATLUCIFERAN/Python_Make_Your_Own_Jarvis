
# The complex system status data (a nested dictionary)
system_status = {
    "core": {"temp": 45, "load": 0.25, "active": True},
    "peripherals": [
        {"name": "camera", "status": "online", "users": ["T", "P"]},
        {"name": "mic_array", "status": "offline", "reason": "user_override"}
    ],
    "log_size": 192801
}

# 1. The painful, standard way:
print("--- Standard Print ---\n", system_status)

# 2. The organized, J.A.R.V.I.S. way:
import pprint
pprint.pprint(system_status)