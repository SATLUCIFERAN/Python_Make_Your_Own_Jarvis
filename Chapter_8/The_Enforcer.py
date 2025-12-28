
from pydantic import BaseModel, Field

# 1. Define the model using Pydantic's BaseModel

class SystemHealth(BaseModel):
    device: str
    temp_celsius: int = Field(alias="temp") 

corrupted_data = {
    "device": "Core Reactor",
    "temp": "95"  
}

try:    
    health_report = SystemHealth.model_validate(corrupted_data)
    print("Report validated" 
          f"Reactor temp type is now: {type(health_report.temp_celsius)}")
except Exception as e:
    print(f"Validation Failed! {e}")