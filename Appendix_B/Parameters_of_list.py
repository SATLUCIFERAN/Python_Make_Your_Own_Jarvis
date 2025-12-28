
# Jarvis records task timestamps (earliest to latest)
task_times = [
    1678886400, # Oldest task
    1709424000, # Mid-age task
    1730030400  # Newest task
]

# We want the newest item (largest number) first!
task_times.sort(reverse=True)

# Jarvis Output: Newest first!
print(task_times)
# Output: [1730030400, 1709424000, 1678886400]