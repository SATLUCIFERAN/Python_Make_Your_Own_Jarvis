
import typer
from typing import Optional

def launch(    
    mode: str = typer.Option("live", 
                             help="Selects the operational mode (live or silent)."),
    skip_tests: Optional[bool] = typer.Option(False, 
                                              "--skip-tests", 
                                              help="Skip the startup diagnostics.")
):
    
    if mode == 'live':
        print(f"Starting J.A.R.V.I.S. in LIVE mode.")
    else:
        print(f"Starting J.A.R.V.I.S. in SILENT mode.")
        
    if skip_tests:
        print("Bypassing diagnostics...")

if __name__ == "__main__":
    typer.run(launch)


    