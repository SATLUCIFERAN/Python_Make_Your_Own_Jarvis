
system_status = "Online"
system_load = 0.55

# The indented block belongs to the 'if' statement
if system_load > 0.5:
    print("Warning: High system load detected.") 
# This line is not indented, so it runs regardless of the condition
print("Checking peripherals.")