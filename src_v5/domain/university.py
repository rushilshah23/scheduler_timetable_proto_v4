from dataclasses import dataclass
from typing import Dict, List, Literal, Union, Set
from datetime import time
from typing import List
from datetime import timedelta
from abc import ABC, abstractmethod
import copy
from src_v5.ga import Gene

import math

def create_slots_for_division(division: 'Division') -> List['Slot']:
    working_week_skeleton = division.working_week_skeleton
    slots = []
    slot_duration = working_week_skeleton.slot_duration  # Get slot duration from the skeleton
    
    # Iterate through each working day in the skeleton
    for working_day in working_week_skeleton.working_days:
        for working_hour in working_day.working_hours:
            current_time = working_hour.start_time
            end_time = working_hour.end_time
            
            # Generate slots based on slot_duration
            while current_time < end_time:
                # Calculate the end time for the current slot
                slot_end_time = (datetime.combine(datetime.min, current_time) + 
                                 timedelta(minutes=slot_duration)).time()
                
                # Ensure the slot does not exceed the working hour's end time
                if slot_end_time > end_time:
                    # slot_end_time = end_time
                    raise Exception("Timings need to be in sync with schedule size")
                
                # Create a new WorkingHours instance for the slot
                slot_time = WorkingHours(
                    id=get_new_id(),  # Generate a unique ID for the slot time
                    start_time=current_time,
                    end_time=slot_end_time
                )
                
                # Create a new Slot object and add it to the list
                slot_id = get_new_id()  # Generate a unique ID for the slot
                slots.append(Slot(
                    id=slot_id,
                    working_day=working_day,
                    slot_time=slot_time,
                    slot_duration=slot_duration,  # Add the slot duration
                    slot_alloted_to=None , # No entity is allocated initially
                    division= division
                ))
                
                # Move to the next slot's start time
                current_time = slot_end_time

    return slots


def create_slot_allotables_for_entities(entities: List['Entity']) -> List['SlotAllotable']:
    slot_allotables = []

    for entity in entities:
        # Determine how many sets of SlotAllotable objects to create
        num_sets = int(math.floor(entity.maximum_weekly_frequency / entity.continuous_slot))
        for k in range(num_sets):
            current_slot_allotable = None

            for i in range(entity.continuous_slot):
                # Create a new SlotAllotable
                slot_allotable = SlotAllotable(
                    id=get_new_id(),
                    allotable_entity=entity,
                    next_slot_allotable=None,  # Always None initially
                    working_day='auto',       # Replace 'auto' with computed value if needed
                    working_hours='auto',     # Replace 'auto' with computed value if needed
                    continuous_left=entity.continuous_slot - i - 1  # Remaining slots in the sequence
                )

                # Link the previous SlotAllotable to the current one
                if current_slot_allotable is not None:
                    current_slot_allotable.next_slot_allotable = slot_allotable

                current_slot_allotable = slot_allotable
                slot_allotables.append(current_slot_allotable)
                # slot_allotables.append(slot_allotable)

    return slot_allotables





@dataclass
class Day:
    id:str
    name:str

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }


@dataclass
class WorkingHours:
    id:str
    start_time:time
    end_time:time


    def to_dict(self):
        return {
            "id": self.id,
            "start_time": self.start_time.strftime("%H:%M:%S"),
            "end_time": self.end_time.strftime("%H:%M:%S")
        }

@dataclass
class WorkingDay:
    id:str
    day:Day
    working_hours:Set[WorkingHours] = None

    def __post_init__(self):
        if self.working_hours is None:
            self.working_hours = set()

    def to_dict(self):
        return {
            "id": self.id,
            "day": self.day.to_dict(),
            "working_hours": [wh.to_dict() for wh in self.working_hours]
        }

@dataclass
class WorkingWeekSkeleton:
    id:str
    slot_duration:int
    working_days: List[WorkingDay] = None

    def __post_init__(self):
        if self.working_days is None:
            self.working_days = []

    def add_working_day(self, working_day:WorkingDay):
        for curr_working_day in self.working_days:
            if curr_working_day.day.id == working_day.day.id:
                raise Exception(f"Working week already has data for day {curr_working_day.day.name}")

    def to_dict(self):
        return {
            "id":self.id,
            "slot_duration": self.slot_duration,
            "working_days": [wd.to_dict() for wd in self.working_days],
        }
    

@dataclass
class Division():
    id:str
    name:str
    university:'University'
    working_week_skeleton:WorkingWeekSkeleton= None

    def __post_init__(self):
        if self.working_week_skeleton is None:
            self.working_week_skeleton = self.university.working_week_skeleton
            if self.working_week_skeleton is not None:
                self.working_week_skeleton.division = self


    def set_working_week_skeleton(self, working_week_skeleton):
        self.working_week_skeleton = working_week_skeleton


    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "university": self.university.to_dict(),
            "working_week_skeleton": self.working_week_skeleton.to_dict() if self.working_week_skeleton else None
        }

@dataclass
class University():
    id:str
    logo_path:Union[str, Literal[None]]
    name:str
    working_week_skeleton:WorkingWeekSkeleton = None

    def set_working_week_skeleton(self, working_week_skeleton:WorkingWeekSkeleton):
        self.working_week_skeleton = working_week_skeleton

    def add_division(division):
        pass

    def add_subject(subject):
        pass

    def add_faculty(faculty):
        pass

    def to_dict(self):
        return {
            "id": self.id,
            "logo_path": self.logo_path,
            "name": self.name,
            "working_week_skeleton": self.working_week_skeleton.to_dict() if self.working_week_skeleton else None
        }



@dataclass
class Subject:
    id: str
    name: str

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }


@dataclass
class Faculty:
    id: str
    name: str
    availability_skeleton: 'WorkingWeekSkeleton'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "availability_skeleton": self.availability_skeleton.to_dict() if self.availability_skeleton else None

        }


@dataclass
class Entity(ABC):
    id: str
    continuous_slot:int
    maximum_weekly_frequency:int


    def __post_init__(self):
        if self.maximum_weekly_frequency < self.continuous_slot:
            raise Exception(f"Continuous slot count can't be greater than maximum weekly frequency")

    @abstractmethod
    def to_dict(self):
        pass


@dataclass
class TeachingEntity(Entity):
    subject: Subject
    faculty: Faculty
    division: Division
    type = 'TeachingEntity'


    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "subject": self.subject.to_dict(),
            "faculty": self.faculty.to_dict(),
            "division": self.division.to_dict(),
            "continuous_slots":self.continuous_slot,
            "maximum_weekly_frequency":self.maximum_weekly_frequency
        }


@dataclass
class NonTeachingEntity(Entity):
    name: str
    division: Division
    type = 'NonTeachingEntity'

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "continuous_slots":self.continuous_slot,
            "maximum_weekly_frequency":self.maximum_weekly_frequency,
            "division": self.division.to_dict(),

        }


@dataclass
class EmptyEntity(Entity):
    name: str = 'EMPTY'
    type = 'EmptyEntity'

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "continuous_slots":self.continuous_slot,
            "maximum_weekly_frequency":self.maximum_weekly_frequency,

        }


@dataclass
class Slot(Gene):
    id: str
    working_day: WorkingDay
    slot_time:WorkingHours
    slot_duration:int
    division:Division
    slot_alloted_to: 'SlotAllotable' = None
    

    def to_dict(self):
        return {
            "id": self.id,
            "slot_alloted_to": self.slot_alloted_to.to_dict() if self.slot_alloted_to else None,
            "working_day": self.working_day.to_dict(),
            "slot_duration":self.slot_duration,
            "slot_time":self.slot_time.to_dict(),
            "division":self.division.to_dict()

        }
    


@dataclass
class SlotAllotable:
    id:str
    allotable_entity:Union[TeachingEntity | NonTeachingEntity | EmptyEntity]
    next_slot_allotable:'SlotAllotable'
    continuous_left:int
    working_day:Union[WorkingDay,Literal['auto']]= 'auto'
    working_hours:Union[WorkingHours,Literal['auto']] ='auto'

    def to_dict(self):
        return {
            "allotable_entity":self.allotable_entity.to_dict(),
            "next_slot_allotable":self.next_slot_allotable.to_dict() if self.next_slot_allotable else self.next_slot_allotable,
            "working_day":self.working_day.to_dict() if self.working_day != 'auto' else self.working_day,
            "working_hours":self.working_hours.to_dict() if self.working_hours != 'auto' else self.working_hours,
            "continuous_left":self.continuous_left

        }
    



from src_v5.utils.generic_utils import *

@dataclass
class Orchestra():
    def create_university(self, name, logo_path=None):
        new_id = get_new_id()
        university = University(id=new_id, logo_path=logo_path, name=name)
        return university
    

    def create_division_for_university(self,name:str, university:University):
        new_id = get_new_id()
        division = Division(id=new_id, name=name, university=university)
        return division
    
    def create_slots_for_division(self, division:Division):
        slots:List[Slot] = create_slots_for_division(division=division)
        return slots
    
    def create_slot_allotables_for_entities(self, entities:List[Entity]):
        slot_allotables:List[Slot] = create_slot_allotables_for_entities(entities=entities)
        return slot_allotables
        
        
    def clone_working_week_skeleton(self, working_week_skeleton: WorkingWeekSkeleton):
        new_working_week_skeleton = copy.deepcopy(working_week_skeleton)
        new_working_week_skeleton.id = get_new_id()

        for i, working_day in enumerate(new_working_week_skeleton.working_days):
            working_day.id = get_new_id()

            for j, working_hour in enumerate(working_day.working_hours):
                working_hour.id = get_new_id()
                working_day.working_hours[j] = working_hour  # Update the list element

            new_working_week_skeleton.working_days[i] = working_day  # Update the list element

        return new_working_week_skeleton




    def to_dict(self):
        return {}



