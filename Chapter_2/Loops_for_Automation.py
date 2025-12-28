
command_list = ["check_temp", "send_email", "log_status"]

for command in command_list:
    print(f"Executing: {command}")

for i in range(3):
    print(f"Retrying connection... ({i + 1})")