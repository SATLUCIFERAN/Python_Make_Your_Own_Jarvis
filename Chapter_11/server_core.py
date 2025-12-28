
from fastapi import FastAPI


app = FastAPI()

@app.get("/status")
def get_system_status():
    """Reports the simple operational status of J.A.R.V.I.S."""
    return {
        "status": "Operational",
        "load": 0.25,
        "mode": "Live"
    }