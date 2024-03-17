import base64
import cv2
import inspect
import time
import logging
import os

logger = logging.getLogger(__name__)

def timing_decorator(func):
    """Decorator to measure the duration of a function call."""
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()  # Record start time
        result = func(*args, **kwargs)  # Call the actual function
        end_time = time.time()  # Record end time
        duration = end_time - start_time  # Calculate duration
        logger.info(f"{func.__name__} ran in: {duration:.4f} seconds")
        return result
    async def async_wrapper(self, *args, **kwargs):
        start_time = time.time()  # Record start time
        result = await func(self, *args, **kwargs)  # Call the actual function
        end_time = time.time()  # Record end time
        duration = end_time - start_time  # Calculate duration
        logger.info(f"{func.__name__} ran in: {duration:.4f} seconds")
        return result
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def time_to_seconds(time_str):
  """Function to convert HH:MM:SS.SSS format to seconds"""
  h, m, s = time_str.split(':')
  return int(h) * 3600 + int(m) * 60 + float(s)


def read_file(fpath, econding = 'utf-8'):
    with open(fpath, 'r', encoding=econding) as f:
        template = f.read()
    return template

def convert_img_b64(img):
    _, buffer = cv2.imencode('.jpeg', img[..., ::-1]) # invert from RGB to BGR
    image_base64 = base64.b64encode(buffer)
    image_string = str(image_base64)[2:-1] # Turning into clean string for prompt
    return image_string

def create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.mkdir(directory_path)