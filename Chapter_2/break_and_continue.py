
system_alerts = ["temp_ok", "skip_log", "temp_ok", "CRITICAL_FAILURE", "temp_ok"]

for alert in system_alerts:
    if alert == "skip_log":
        print(f"ALERT: Skipping malformed log entry.")
        continue
    
    if alert == "CRITICAL_FAILURE":
        print(f"FATAL ERROR: Immediate system shutdown required!")
        break
        
    print(f"Log: Processing alert: {alert}")

print("Monitoring stopped.")