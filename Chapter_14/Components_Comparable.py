
class SystemAlert:
    """
    Represents a system alert where priority is determined by severity.
    """
    def __init__(self, code: str, severity: int):
        self.code = code
        self.severity = severity
    
    def __str__(self):
        return f"Alert {self.code} (Severity: {self.severity})"

    
    def __eq__(self, other) -> bool:
        """Alerts are equal if their severity matches."""        
        if isinstance(other, SystemAlert):
            return self.severity == other.severity
        return NotImplemented

    
    def __gt__(self, other) -> bool:
        """Alert A is 'greater' (higher priority) than Alert B."""       
        if isinstance(other, SystemAlert):
            return self.severity > other.severity
        return NotImplemented

# --- Usage ---

alert_minor = SystemAlert("FAN", severity=3)
alert_critical = SystemAlert("CORE", severity=8)
alert_same_level = SystemAlert("SHIELD", severity=3)

print(f"Minor == Same Level? {alert_minor == alert_same_level}") 
print(f"Critical > Minor? {alert_critical > alert_minor}")  
print(f"Minor < Critical? {alert_minor < alert_critical}") 
