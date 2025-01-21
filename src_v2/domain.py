from dataclasses import dataclass, field
from typing import List, Optional
from datetime import time
from enum import Enum
from abc import  ABC, abstractmethod
from src_v2.ga import Gene, Chromosome
from src_v2.rules import *



@dataclass
class Day:
    id: str
    name: str


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

@dataclass
class WorkingDay:
    id: str
    day_id: str
    start_time: time  # You can use datetime if you need more control
    end_time: time
    slot_duration: int
    division_id:str


    day: Day
    division:'Division'
    

    def to_dict(self):
        return {
            "id": self.id,
            "day_id": self.day_id,
            "start_time": self.start_time.strftime("%H:%M:%S"),
            "end_time": self.end_time.strftime("%H:%M:%S"),
            "slot_duration": self.slot_duration,
            "division_id":self.division_id,
            "day": self.day.to_dict(),
            "division":self.division.to_dict()
        }

@dataclass
class Slot(Gene):
    id: str
    start_time: time
    end_time: time
    working_day_id: str
    daily_slot_number:int
    weekly_slot_number:int

    working_day: WorkingDay
    slot_alloted_to_allotable: "SlotAllotable" = None
    slot_alloted_to_allotable_id:str=None



    def to_dict(self):
        return {
            "id": self.id,
            "start_time": self.start_time.strftime("%H:%M:%S"),
            "end_time": self.end_time.strftime("%H:%M:%S"),
            "working_day_id": self.working_day_id,
            "daily_slot_number":self.daily_slot_number,
            "weekly_slot_number":self.weekly_slot_number,
            "slot_alloted_to_allotable_id":self.slot_alloted_to_allotable_id,
            "working_day": self.working_day.to_dict() if self.working_day else None,
            "slot_alloted_to_allotable": self.slot_alloted_to_allotable.to_dict() if self.slot_alloted_to_allotable else None,
        }

@dataclass
class SlotAllotable:
    id: str
    division_id: str
    next_slot_allotable_id: str
    working_day_id:Union[str, None]
    division: 'Division'
    next_slot_allotable: 'SlotAllotable'

    allotable_entity_id: str
    allotable_entity: "AllotableEntity"

    working_day_rule: WorkingDayRule
    start_time_rule: StartTimeRule
    end_time_rule: EndTimeRule
    continuous_slot_rule: ContinuousSlotRule
    minimum_daily_frequency_rule: MinimumDailyFrequencyRule
    maximum_daily_frequency_rule: MaximumDailyFrequencyRule
    minimum_weekly_frequency_rule: MinimumWeeklyFrequencyRule
    maximum_weekly_frequency_rule: MaximumDailyFrequencyRule
    working_day: Union['WorkingDay', None]

    def to_dict(self):
        return {
            "id": self.id,
            "division_id": self.division_id,
            "next_slot_allotable_id": self.next_slot_allotable_id,
            "division": self.division.to_dict() if self.division else None,
            "next_slot_allotable": self.next_slot_allotable.to_dict() if self.next_slot_allotable else None,
            "allotable_entity_id": self.allotable_entity_id,
            "allotable_entity": self.allotable_entity.to_dict() if self.allotable_entity else None,
            "working_day_rule": self.working_day_rule.to_dict() if self.working_day_rule else None,
            "start_time_rule": self.start_time_rule.to_dict() if self.start_time_rule else None,
            "end_time_rule": self.end_time_rule.to_dict() if self.end_time_rule else None,
            "continuous_slot_rule": self.continuous_slot_rule.to_dict() if self.continuous_slot_rule else None,
            "minimum_daily_frequency_rule": self.minimum_daily_frequency_rule.to_dict() if self.minimum_daily_frequency_rule else None,
            "maximum_daily_frequency_rule": self.maximum_daily_frequency_rule.to_dict() if self.maximum_daily_frequency_rule else None,
            "minimum_weekly_frequency_rule": self.minimum_weekly_frequency_rule.to_dict() if self.minimum_weekly_frequency_rule else None,
            "maximum_weekly_frequency_rule": self.maximum_weekly_frequency_rule.to_dict() if self.maximum_weekly_frequency_rule else None,
            "working_day": self.working_day.to_dict() if self.working_day else None,
            "working_day_id": self.working_day_id if self.working_day_id else None,

        }
 






@dataclass
class AllotableEntity():
    id:str
    name:str

    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name
        }

@dataclass
class Break(AllotableEntity):
    def to_dict(self):
        base_dict = super().to_dict()
        return base_dict



@dataclass
class Proxy(AllotableEntity):
    def to_dict(self):
        base_dict = super().to_dict()
        return base_dict



@dataclass
class Faculty:
    id: str
    name: str
    university_id:str
 
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "university_id":self.university_id
        }
    


@dataclass
class Subject:
    id: str
    name: str
    university_id:str

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "university_id":self.university_id

        }

@dataclass
class Division:
    id: str
    name: str
    university_id:str
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "university_id": self.university_id,
        }







@dataclass
class University:
    id: str
    name: str
    logo:str

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "logo":self.logo
        }


@dataclass
class FacultySubjectDivision(AllotableEntity):
    faculty_id: str
    subject_id: str
    division_id: str

    faculty:Faculty
    subject:Subject
    division:Division



    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
        
            "faculty_id": self.faculty_id,
            "subject_id": self.subject_id,
            "division_id": self.division_id,
            "faculty": self.faculty.to_dict() if self.faculty else None,
            "subject": self.subject.to_dict() if self.subject else None,
            "division": self.division.to_dict() if self.division else None
            
        })
        return base_dict

