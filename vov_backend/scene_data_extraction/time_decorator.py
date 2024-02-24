import time

def timing_decorator(func):
    """Decorator to measure the duration of a function call."""
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record start time
        result = func(*args, **kwargs)  # Call the actual function
        end_time = time.time()  # Record end time
        duration = end_time - start_time  # Calculate duration
        print(f"{func.__name__} ran in: {duration} seconds")
        return result
    return wrapper
