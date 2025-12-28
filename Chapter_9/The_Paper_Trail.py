
import logging


logging.basicConfig(
    level=logging.INFO, 
    filename='system_report.log', 
    filemode='a', 
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s' 
)


core_logger = logging.getLogger('CORE_SYSTEM')
core_logger.info("Core module initialization complete.")
core_logger.warning("Low memory alert: 15%% remaining.")


def attempt_division(numerator, denominator):
    try:
        core_logger.info("Attempting critical calculation.")
        result = numerator / denominator
        core_logger.info(f"Calculation successful. Result: {result}")
    except ZeroDivisionError:        
        core_logger.exception("Failed to calculate division due to zero input.")
        
attempt_division(10, 0)