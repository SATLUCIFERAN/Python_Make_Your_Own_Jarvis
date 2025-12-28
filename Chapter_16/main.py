
from core import chat
import uuid

# --- APPLICATION LAUNCH ---

if __name__ == "__main__":    
    session_id = str(uuid.uuid4())[:8]   
    chat(session_id)

# When you run this file, the 'chat' function takes over.