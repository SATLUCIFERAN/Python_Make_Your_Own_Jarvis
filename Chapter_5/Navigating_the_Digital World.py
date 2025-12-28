
from pathlib import Path


base_dir = Path.cwd()
config_file = base_dir / "config" / "user_settings.json"
print(f"J.A.R.V.I.S. is looking for config at: {config_file}")


if config_file.exists():
    print("Verification: File found.")
else:
    print("Alert: Configuration file is missing. Initialization halted.")