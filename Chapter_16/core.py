

from skills import SKILLS # We'll define SKILLS in the next step

def chat(user_id):    
    print("Jarvis Activated. Start talking (or type 'quit' or 'exit').")
    
    # The infinite loop that keeps the conversation going
    while True:
        try:
            # 1. Get Input: Replace with microphone later
            user_input = input(f"[{user_id}] > ").strip().lower()

            if user_input in ['quit', 'exit']:
                print("Jarvis shutting down. Have a productive day.")
                break

            # 2. Routing Logic: The MVP Switchboard
            # We check if the user's input matches any skill keys
            if user_input in SKILLS:
                skill_func = SKILLS[user_input]
                # EXECUTION: Call the linked function and get the result
                response = skill_func()
                print(f"Jarvis: {response}")
            
            else:
                # Default response (the AI placeholder)
                print("Jarvis: I'm currently focused on core functions. Try asking me the 'time'.")
                
        except Exception as e:
            # Basic error handling to keep the loop running
            print(f"Jarvis Error: A system error occurred: {e}")

# This core.py file should only contain routing and logic functions.
