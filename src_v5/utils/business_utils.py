from enum import Enum
from datetime import time, timedelta

class DayEnum(Enum):
    monday = {"id": 1, "value": "monday"}
    tuesday = {"id": 2, "value": "tuesday"}
    wednesday = {"id": 3, "value": "wednesday"}
    thursday = {"id": 4, "value": "thursday"}
    friday = {"id": 5, "value": "friday"}
    saturday = {"id": 6, "value": "saturday"}
    sunday = {"id": 7, "value": "sunday"}

    @staticmethod
    def get_day_id(day_name: str) -> int:
        try:
            day_name = day_name.lower()
            return DayEnum[day_name].value["id"]
        except KeyError:
            raise ValueError(f"Invalid day name: {day_name}")

def is_time_colliding(
    slot_start_time: time,
    slot_end_time: time,
    next_slot_day_id: int,
    next_slot_start_time: time,
    next_slot_end_time: time,
) -> bool:
    """
    Checks if two slots collide or include each other based on their day and time ranges.
    
    Args:
        slot_day_id (int): Day ID of the first slot.
        slot_start_time (time): Start time of the first slot.
        slot_end_time (time): End time of the first slot.
        next_slot_day_id (int): Day ID of the second slot.
        next_slot_start_time (time): Start time of the second slot.
        next_slot_end_time (time): End time of the second slot.
        
    Returns:
        bool: True if slots collide or include each other, False otherwise.
    """
    # Check if slots are on the same day


    # Check if slots collide or include
    if (slot_start_time < next_slot_end_time and slot_end_time > next_slot_start_time):
        return True

    return False


def is_time_including(start_time_1,end_time_1,start_time_2, end_time_2):
    if start_time_1 <= start_time_2 and end_time_1 >= end_time_2:
        return True
    


def get_timings_wrt_slotsize(start_time: time, end_time: time, slot_size: int):
    """
    Generates sequential time slots between start_time and end_time based on slot_size.

    Args:
        start_time (time): The starting time of the range.
        end_time (time): The ending time of the range.
        slot_size (int): The duration of each slot in minutes.

    Returns:
        List[dict]: A list of dictionaries representing the time slots.
    """
    slots = []
    current_time = timedelta(hours=start_time.hour, minutes=start_time.minute)
    end_time_delta = timedelta(hours=end_time.hour, minutes=end_time.minute)

    while current_time + timedelta(minutes=slot_size) <= end_time_delta:
        slot_start = current_time
        slot_end = current_time + timedelta(minutes=slot_size)

        slots.append({
            "start_time": (slot_start.seconds // 3600, (slot_start.seconds % 3600) // 60),
            "end_time": (slot_end.seconds // 3600, (slot_end.seconds % 3600) // 60)
        })

        current_time = slot_end

    return slots


