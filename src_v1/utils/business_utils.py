from enum import Enum


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

