
raw_history = ["READ STATUS", "", "set volume 5", "read status"]

valid_commands = [command.lower() for command in raw_history if command != ""]
print(valid_commands)
unique_commands = {command for command in valid_commands}
print(unique_commands)