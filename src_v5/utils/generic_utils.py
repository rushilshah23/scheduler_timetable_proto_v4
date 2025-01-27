import os
import json
import time as tmod  # Rename time module to avoid conflict
import uuid
from datetime import timezone, datetime, time

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        return super().default(obj)

def save_output_file(file_name, data):

    curr_dir = os.path.abspath(os.path.dirname(__file__))
    output_dir = os.path.join(curr_dir, '../data/outputs')
    file_path = os.path.join(output_dir,file_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # with open(file_path,'w') as json_file:
    #     json.dump(data, json_file,default=lambda obj: obj.to_dict(), indent=4)
    with open(file_path,'w') as fp:
        json.dump(data,fp,cls=CustomEncoder, indent=4)
    

def timer(func):
    """A decorator to measure the time a function takes to execute."""
    
    def wrapper(*args, **kwargs):
        start_time = tmod.time()  # Use tmod to avoid conflict with datetime.time
        
        result = func(*args, **kwargs)  # Execute the function
        end_time = tmod.time()  # Use tmod to avoid conflict with datetime.time
        elapsed_time = end_time - start_time  # Calculate the time difference
        print(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds.")
        return result  # Return the result of the function call
    return wrapper

def get_new_id():
    return str(uuid.uuid4())


from datetime import datetime, time

def convert_str_to_time(time_str: str, time_format: str = "%I:%M %p") -> time:
    """
    Converts a time string to a time object and returns it in 24-hour format.
    Handles time strings with or without seconds and adjusts formats accordingly.
    :param time_str: The time string to convert.
    :param time_format: The format to parse the time string (default: "%I:%M %p").
    :return: A time object.
    """
    try:
        # Normalize the time string by removing seconds if present
        if ":" in time_str and time_str.count(":") == 2:
            time_str = ":".join(time_str.split(":")[:2])
        
        # Ensure consistency in AM/PM format
        time_str = time_str.upper().replace("AM", " AM").replace("PM", " PM").strip()

        # Handle common formats dynamically
        possible_formats = [time_format, "%H:%M"]  # Add other formats if needed

        for fmt in possible_formats:
            try:
                return datetime.strptime(time_str, fmt).time()
            except ValueError:
                continue
        
        # Raise an error if no format matches
        raise ValueError(f"Time string '{time_str}' does not match any known formats.")
    except Exception as e:
        raise ValueError(f"Error processing time string '{time_str}': {e}")

def convert_datetime_to_utc_datetime(local_time: datetime) -> datetime:
    """
    Converts a given datetime to UTC.

    :param local_time: A datetime object in local time.
    :return: A datetime object converted to UTC.
    """
    if local_time.tzinfo is None:
        raise ValueError("The provided datetime must be timezone-aware.")
    return local_time.astimezone(timezone.utc)


def calculate_sum(n):
    return sum(range(1, n + 1))

def factorial(n):
    if n==1:
        return 1
    return n * factorial(n-1)



class TimeDifferenceError(ValueError):
    """Custom exception for invalid time differences."""
    pass

def get_time_difference_in_seconds(start_time: time, end_time: time) -> int:
    # Check if start_time is greater than end_time
    if start_time > end_time:
        raise TimeDifferenceError("start_time cannot be greater than end_time")
    
    # Convert time objects to datetime objects for the same day
    today = datetime.today()
    start_datetime = datetime.combine(today, start_time)
    end_datetime = datetime.combine(today, end_time)
    
    # Calculate the time difference
    time_difference = end_datetime - start_datetime
    
    # Return the difference in seconds
    return int(time_difference.total_seconds())


def read_json_data(file_path: str):
    """
    Reads JSON data from a file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON data.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data