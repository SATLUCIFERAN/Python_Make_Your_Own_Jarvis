

def generate_greeting(user_name: str, time_of_day: str):    
    return f"Good {time_of_day}, {user_name}. Systems operational."


morning_message = generate_greeting("Tony", "Morning")
evening_message = generate_greeting("Pepper", "Evening")

print(morning_message)
print(evening_message)