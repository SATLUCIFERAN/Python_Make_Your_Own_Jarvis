
daily_tasks = [
    ("Medium", 1400, "Review Python code"),  # Medium, 2:00 PM
    ("High",   900,  "Read morning brief"),  # High, 9:00 AM
    ("Medium", 1030, "Schedule next chat"),  # Medium, 10:30 AM
    ("High",   1400, "System backup"),       # High, 2:00 PM
]
priority_map = {"High": 1, "Medium": 2, "Low": 3}


daily_tasks.sort(key=lambda x: (priority_map[x[0]], x[1]))
print("\n--- JARVIS DAILY TASK QUEUE ---")
for task in daily_tasks:
    print(f"[{task[0].upper():<6}] {task[1]:<5} - {task[2]}")


# Output:
# [HIGH  ] 900   - Read morning brief
# [HIGH  ] 1400  - System backup
# [MEDIUM] 1030  - Schedule next chat
# [MEDIUM] 1400  - Review Python code