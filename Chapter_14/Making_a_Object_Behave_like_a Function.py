
class FireControl:
    """
    Represents a highly configured weapon system that is executed like a function.
    """
    def __init__(self, primary_target_list: list):        
        self.target_list = primary_target_list
        self.status = "Armed and Ready"

    def __call__(self, threat_id: str):        
        if threat_id in self.target_list:
            print(f"[{self.status}] Engaging priority threat: {threat_id}")           
            self.status = "Firing Sequence Active"
            return True
        else:
            print(f"[{self.status}] Threat {threat_id} not on priority list. Standby.")
            return False


fire_control = FireControl(primary_target_list=["K-940", "A-113", "B-201"])

print(f"Initial Status: {fire_control.status}")
fire_control("K-940")
fire_control("X-777")
print(f"Final Status: {fire_control.status}")
