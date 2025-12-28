
# Jarvis check: Return 'Active' or 'Standby' status
check_status = lambda status_code: "Active" if status_code == 1 else "Standby"
print(check_status(0)) 