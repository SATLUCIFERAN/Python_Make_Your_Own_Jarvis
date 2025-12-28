
from fastapi import FastAPI
from pydantic import BaseModel


class Command(BaseModel):   
    text: str    
    priority: int = 1 



app = FastAPI()

@app.get("/status")
def get_system_status():
    """Reports the simple operational status of J.A.R.V.I.S."""
    return {
        "status": "Operational",
        "load": 0.25,
        "mode": "Live"
    }

# POST Route: Accepts a new command and validates it using the Command model

@app.post("/command")
def process_new_command(command_data: Command):
    """Accepts and processes a structured command from a client"""    
    print(f"Received new command: \
          {command_data.text} (Priority: {command_data.priority})")    
   
    if command_data.priority > 5:
        return {"result": \
                f"High priority command '{command_data.text}' received and queued"}
    else:
        return {"result": \
                f"Standard command '{command_data.text}' processed"}
