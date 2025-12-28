
import datetime

# --- SKILL LIBRARY ---
# This dictionary maps the user command string (key) to the function that executes the task (value).

SKILLS = {}

def skill_telltime():
    """Returns the current local time."""
    now = datetime.datetime.now()    
    formatted_time = now.strftime("The current time is %I:%M %p on %A.")
    return formatted_time

# --- REGISTRATION ---
# Register the function with the main SKILLS dictionary
# The key 'time' is the command the core logic will recognize.

SKILLS['time'] = skill_telltime

# You can register multiple commands to the same function:

SKILLS['what time is it'] = skill_telltime