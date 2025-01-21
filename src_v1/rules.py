from dataclasses import dataclass, field
from typing import Literal, Union, List
from datetime import time  
from enum import Enum
from abc import abstractmethod


class AutoTypeEnum(Enum):
    auto = "auto"

class RuleTypesEnum(Enum):
    hard = "hard"
    soft = "soft"


@dataclass
class Rule:
    priority: int = 1
    type: RuleTypesEnum = RuleTypesEnum.hard

    def __post_init__(self):
        if self.type is RuleTypesEnum.hard:
            self.priority = 1


    def to_dict(self):
        return {
            'priority':self.priority,
            'type':self.type.value
        }


@dataclass
class WorkingDayRule(Rule):
    working_day_id: Union[str, AutoTypeEnum] = AutoTypeEnum.auto

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'working_day_id': self.working_day_id if isinstance(self.working_day_id, str) else self.working_day_id.value
        }


@dataclass
class StartTimeRule(Rule):
    start_time: Union[time, AutoTypeEnum] = AutoTypeEnum.auto

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'start_time':self.start_time.strftime("%H:%M:%S") if isinstance(self.start_time, time) else self.start_time.value,
        }


@dataclass
class EndTimeRule(Rule):
    end_time: Union[time, AutoTypeEnum] = AutoTypeEnum.auto

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'end_time':self.end_time.strftime("%H:%M:%S") if isinstance(self.end_time, time) else self.end_time.value,

        }


@dataclass
class ContinuousSlotRule(Rule):
    continuous_slot: Union[int, AutoTypeEnum] = AutoTypeEnum.auto

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'continuous_slot': self.continuous_slot if isinstance(self.continuous_slot, int) else self.continuous_slot.value
        }


@dataclass
class MinimumDailyFrequencyRule(Rule):
    min_daily_frequency: Union[int, AutoTypeEnum] = AutoTypeEnum.auto

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'min_daily_frequency': self.min_daily_frequency if isinstance(self.min_daily_frequency, int) else self.min_daily_frequency.value
        }


@dataclass
class MaximumDailyFrequencyRule(Rule):
    max_daily_frequency: Union[int, AutoTypeEnum] = AutoTypeEnum.auto

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'max_daily_frequency': self.max_daily_frequency if isinstance(self.max_daily_frequency, int) else self.max_daily_frequency.value
        }


@dataclass
class MinimumWeeklyFrequencyRule(Rule):
    min_weekly_frequency: Union[int, AutoTypeEnum] = AutoTypeEnum.auto

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'min_weekly_frequency': self.min_weekly_frequency if isinstance(self.min_weekly_frequency, int) else self.min_weekly_frequency.value
        }


@dataclass
class MaximumWeeklyFrequencyRule(Rule):
    max_weekly_frequency: Union[int, AutoTypeEnum] = AutoTypeEnum.auto

    def to_dict(self):
        base_dict = super().to_dict()
        return {
            **base_dict,
            'max_weekly_frequency': self.max_weekly_frequency if isinstance(self.max_weekly_frequency, int) else self.max_weekly_frequency.value
        }

@dataclass
class DivisionRule(Rule):
    division_id:str = None

    def __post_init__(self):
        if self.division_id is None:
            raise TypeError(f"Divison ID can't be None")

    def to_dict(self):
        base_dict =  super().to_dict()
        return {
            **base_dict,
            'division_id':self.division_id
        }
    
# @dataclass
# class SlotDurationRule(Rule):
#     slot_duration_in_seconds: Union[int, AutoTypeEnum] = AutoTypeEnum.auto

#     def to_dict(self):
#         base_dict = super().to_dict()
#         return {
#             **base_dict,
#             'slot_duration_in_seconds': self.slot_duration_in_seconds if isinstance(self.slot_duration_in_seconds, int) else self.slot_duration_in_seconds.value
#         }




from src.ga import DataPool,Chromosome



@dataclass
class Constraint:
    rule:Rule
    data_pool:DataPool
    penalty_multiplier:int=1

    @abstractmethod
    def apply_constraint(self):
        pass



class WorkingDayConstraint(Constraint):
    def apply_constraint(self,chromosome:Chromosome):
        total_penalty = 0
        current_working_days = {}
        all_working_days = {}

        # Group slots by working day
        for slot in chromosome.genes:
            if slot.working_day_id not in current_working_days:
                current_working_days[slot.working_day_id] = []
            current_working_days[slot.working_day_id].append(slot)

        # for slot in self.data_pool.slots:
        #     if slot.working_day_id not in all_working_days:
        #         all_working_days[slot.working_day_id] = []
        #     all_working_days[slot.working_day_id].append(slot)

        # Iterate through each working day
        for working_day_id, slots in current_working_days.items():
            # Sort slots by start time
            slots.sort(key=lambda x: x.start_time)

            for i in range(len(slots)):
                current_slot = slots[i]
                if current_slot.slot_alloted_to_allotable is None:
                    continue
                elif current_slot.slot_alloted_to_allotable.work_day_rule.working_day_id == AutoTypeEnum.auto:
                    continue
                elif current_slot.slot_alloted_to_allotable.work_day_rule.working_day_id != working_day_id:
                    total_penalty+=1

        return total_penalty * self.penalty_multiplier

class StartTimeConstraint(Constraint):
    def apply_constraint(self):
        print("start time constraint")


def constraint_generator(rule: Rule):
    if isinstance(rule, WorkingDayRule):
        return WorkingDayConstraint(rule)
    elif isinstance(rule, StartTimeRule):
        return StartTimeConstraint(rule)
    else:
        return None

if __name__ == "__main__":
# if __name__ == "src_v2.timetabler_2.constraints.rules":


    rules:List[Rule] = []
    day_rule = WorkingDayRule(working_day_id="123")
    start_time_rule = StartTimeRule(type=RuleTypesEnum.soft)
    print(day_rule)
    print(start_time_rule)

    rules.append(day_rule)
    rules.append(start_time_rule)

    constraints = [constraint_generator(rule) for rule in rules if constraint_generator(rule) is not None]

    for constraint in constraints:
        constraint.apply_constraint()