import time
import logging

logger = logging.getLogger(__name__)

def timing_decorator(func):
    """Decorator to measure the duration of a function call."""
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record start time
        result = func(*args, **kwargs)  # Call the actual function
        end_time = time.time()  # Record end time
        duration = end_time - start_time  # Calculate duration
        logger.info(f"{func.__name__} ran in: {duration:.4f} seconds")
        return result
    return wrapper
