
import argparse

parser = argparse.ArgumentParser(
    description="J.A.R.V.I.S. Core Launcher. Controls startup configuration."
)

parser.add_argument(
    '--mode', 
    type=str,
    default='live', 
    choices=['live', 'silent'], # ONLY accepts 'live' or 'silent'
    help='Selects the operational mode (live or silent).'
)
args = parser.parse_args()

# --- Execution Logic ---

if args.mode == 'live':
    print("Starting J.A.R.V.I.S. in LIVE voice mode...")
else:
    print("Starting J.A.R.V.I.S. in SILENT logging mode...")