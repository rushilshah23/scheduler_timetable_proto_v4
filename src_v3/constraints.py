from src_v3.ga import Constraint
from dataclasses import dataclass
from typing import List
from src_v3.domain import *
from src_v3.utils.business_utils import *
from src_v3.rules import *



class SameFacultyAtMultipleSlots(Constraint):
    
    def apply_constraint(self, chromosome:Chromosome):
        total_penalty = 0
        slots:List[Slot] = chromosome.genes
        for i in range(len(slots)-1):
            slot = slots[i]
            if isinstance(slot.slot_alloted_to_allotable.allotable_entity, FacultySubjectDivision):
                slot_day_id = slot.working_day.day_id
                slot_start_time = slot.start_time
                slot_end_time = slot.end_time
            for j in range(i+1,len(slots)):
                next_slot = slots[j]
                if isinstance(next_slot.slot_alloted_to_allotable.allotable_entity, FacultySubjectDivision):
                    next_slot_day_id = next_slot.working_day.day_id
                    next_slot_start_time = next_slot.start_time
                    next_slot_end_time = next_slot.end_time   
                    if slot_day_id == next_slot_day_id and  (slot_start_time < next_slot_end_time and slot_end_time > next_slot_start_time):
                        total_penalty+=1
        return total_penalty*self.penalty_multiplier
    

class NoSameSlot(Constraint):
    def apply_constraint(self, chromosome:Chromosome):
        total_penalty = 0
        slots:List[Slot] = chromosome.genes
        for i in range(len(slots)-1):
            slot = slots[i]
            for j in range(i+1,len(slots)):
                next_slot = slots[j]   
                if slot.id == next_slot.id:
                    total_penalty+=1
        return total_penalty * self.penalty_multiplier


class NoSameAllotables(Constraint):
    def apply_constraint(self,chromosome:Chromosome):
        total_penalty = 0
        slots:List[Slot] = chromosome.genes
        for i in range(len(slots)-1):
            slot = slots[i]
            for j in range(i+1,len(slots)):
                next_slot = slots[j]   
                if slot.slot_alloted_to_allotable.id == next_slot.slot_alloted_to_allotable.id:
                    total_penalty+=1
        return total_penalty * self.penalty_multiplier      
         
class FixedSlotAndSlotAllotableTimeMapping(Constraint):
    def apply_constraint(self,chromosome:Chromosome):
        total_penalty = 0
        slots:List[Slot] = chromosome.genes
        for i in range(len(slots)-1):
            slot = slots[i]
            if slot.slot_alloted_to_allotable.start_time_rule.start_time == AutoTypeEnum.auto or slot.slot_alloted_to_allotable.end_time_rule.end_time == AutoTypeEnum.auto:
                continue
            elif not (is_time_including(slot.start_time,slot.end_time, slot.slot_alloted_to_allotable.start_time_rule.start_time, slot.slot_alloted_to_allotable.end_time_rule.end_time) or is_time_colliding(slot.start_time,slot.end_time, slot.slot_alloted_to_allotable.start_time_rule.start_time, slot.slot_alloted_to_allotable.end_time_rule.end_time)): 
                total_penalty+=1
        return total_penalty * self.penalty_multiplier      
                       
class FixedSlotAndSlotAllotableDayMapping(Constraint):
    def apply_constraint(self,chromosome:Chromosome):
        total_penalty = 0
        slots:List[Slot] = chromosome.genes
        for i in range(len(slots)-1):
            slot = slots[i]
            if slot.slot_alloted_to_allotable.working_day_rule.working_day_id == AutoTypeEnum.auto:
                continue
            elif not (slot.slot_alloted_to_allotable.working_day_rule.working_day_id == slot.working_day_id):
                total_penalty+=1
        return total_penalty * self.penalty_multiplier           
            