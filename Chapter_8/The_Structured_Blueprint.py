
from dataclasses import dataclass


@dataclass(frozen=True)
class ISS_Position:
    latitude: str
    longitude: str
    timestamp: int
    

iss_status = ISS_Position(
    latitude="41.56", 
    longitude="-74.12", 
    timestamp=1678886500
)
print(iss_status.latitude)