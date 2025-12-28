

import functools

# Dummy function for demonstration
def check_user_auth() -> bool:
    # In a real system, this would check a token or password
    return False 

def requires_authorization(func):
    """Decorator to enforce security before execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Executing security check for: {func.__name__}")
        if not check_user_auth():
            return "ACCESS DENIED: Authorization failed. Reactor remains online."        
        return func(*args, **kwargs)
    return wrapper

@requires_authorization
def shutdown_reactor():
    """The critical method being protected."""
    return "Reactor Offline. System secured successfully."

# --- Usage ---
# The decorator runs first, fails the auth check (since check_user_auth returns False), 
# and stops execution before the core logic ever runs.

result = shutdown_reactor()
print(result) 