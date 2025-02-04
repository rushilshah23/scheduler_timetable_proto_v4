from dataclasses import dataclass
from src_v5.ga import Constraint, Chromosome
from typing import List, Any
from collections import defaultdict
from src_v5.domain.university import *


def get_next_slot(slot:'Slot', university_slots:List['Slot']):
    for university_slot in university_slots:
        if university_slot.slot_time.start_time == slot.slot_time.end_time and university_slot.working_day.id == slot.working_day.id and slot.division.id == university_slot.division.id:
            return university_slot
    return None   


def get_next_slot(slot: 'Slot', university_slots: List['Slot']):
    # Find the next slot in the same day and division based on time
    for university_slot in university_slots:
        if (
            university_slot.slot_time.start_time == slot.slot_time.end_time
            and university_slot.working_day.id == slot.working_day.id
            and slot.division.id == university_slot.division.id
        ):
            return university_slot
    return None


def get_previous_slot(slot: 'Slot', university_slots: List['Slot']):
    # Find the previous slot in the same day and division based on time
    for university_slot in university_slots:
        if (
            university_slot.slot_time.end_time == slot.slot_time.start_time
            and university_slot.working_day.id == slot.working_day.id
            and slot.division.id == university_slot.division.id
        ):
            return university_slot
    return None

def get_current_slot_from_allotable(slot_allotable:SlotAllotable, university_slots:List[Slot]):
    for university_slot in university_slots:
       if university_slot.slot_alloted_to.id == slot_allotable.id:
           return university_slot
    raise Exception("Allotable doesn't exists in the university pool") 

class NoSlotRepeatedSlotConstraint(Constraint):
    def apply_constraint(self, chromosome: Chromosome):
        slots = chromosome.genes
        seen = set()
        total_penalty = 0
        for slot in slots:
            if slot.id in seen:
                slot.penalty+=1
                total_penalty += 1
            seen.add(slot.id)
        return self.penalty * total_penalty
    

    def repair_chromosome(self, chromosome):
        return chromosome


class NoFacultyOverlapConstraint(Constraint):
    def apply_constraint(self, chromosome: Chromosome):
        total_penalty = 0
        slots:List[Slot] = chromosome.genes
        for i in range(len(slots)-1):
            slot = slots[i]
            next_slot = slots[i+1]
            if slot.slot_alloted_to is not None and next_slot.slot_alloted_to is not None:
                if slot.slot_alloted_to.allotable_entity is not None and next_slot.slot_alloted_to.allotable_entity is not None:
                    if slot.slot_alloted_to.allotable_entity.type == "TeachingEntity" and next_slot.slot_alloted_to.allotable_entity.type == "TeachingEntity":
                        if slot.slot_alloted_to.allotable_entity.faculty.id == next_slot.slot_alloted_to.allotable_entity.faculty.id:
                            slot.penalty+=1
                            total_penalty+=1
        return self.penalty * total_penalty

    def repair_chromosome(self, chromosome):
        slots:List[Slot] = chromosome.genes
        for i in range(len(slots)-1):
            slot = slots[i]
            next_slot = slots[i+1]
            if slot.slot_alloted_to is not None and next_slot.slot_alloted_to is not None:
                if slot.slot_alloted_to.allotable_entity is not None and next_slot.slot_alloted_to.allotable_entity is not None:
                    if slot.slot_alloted_to.allotable_entity.type == "TeachingEntity" and next_slot.slot_alloted_to.allotable_entity.type == "TeachingEntity":
                        if slot.slot_alloted_to.allotable_entity.faculty.id == next_slot.slot_alloted_to.allotable_entity.faculty.id:
                            slot.slot_alloted_to.allotable_entity = self.generic.gene_generator(mutation_mode=True).slot_alloted_to.allotable_entity
        chromosome.genes = slots
        return chromosome



class ContinuousSlotConstraint(Constraint):



    # def apply_constraint(self, chromosome: Chromosome):
    #     total_penalty = 0
    #     university_slots: List[Slot] = chromosome.genes

    #     for slot in university_slots:
    #         allotable = slot.slot_alloted_to

    #         # Case 1: There is a next_slot_allotable
    #         if allotable.next_slot_allotable is not None:
    #             next_slot = get_next_slot(slot=slot, university_slots=university_slots)

    #             # Penalize if next slot is invalid or doesn't match the sequence
    #             if (
    #                 next_slot is None
    #                 or allotable.next_slot_allotable.id != next_slot.slot_alloted_to.id
    #                 or allotable.continuous_left != next_slot.slot_alloted_to.continuous_left + 1
    #             ):
    #                 slot.penalty += allotable.continuous_left

    #                 total_penalty += allotable.continuous_left

    #         # Case 2: Last allotable in the sequence (no next_slot_allotable)
    #         elif allotable.allotable_entity.continuous_slot > 1:
    #             previous_slot = get_previous_slot(slot=slot, university_slots=university_slots)

    #             # Penalize if no previous slot or sequence mismatch
    #             if (
    #                 previous_slot is None
    #                 or previous_slot.slot_alloted_to.next_slot_allotable is None
    #                 or previous_slot.slot_alloted_to.next_slot_allotable.id != allotable.id
    #                 or allotable.continuous_left != previous_slot.slot_alloted_to.continuous_left - 1
    #             ):
    #                 slot.penalty += allotable.allotable_entity.continuous_slot - 1
                    
    #                 total_penalty += allotable.allotable_entity.continuous_slot - 1

    #     return self.penalty * total_penalty


    def apply_constraint(self, chromosome: Chromosome):
        total_penalty = 0
        university_slots: List[Slot] = chromosome.genes

        for slot in university_slots:
            allotable = slot.slot_alloted_to

            # Case 1: There is a next_slot_allotable
            if allotable.next_slot_allotable is not None:
                next_slot = get_next_slot(slot=slot, university_slots=university_slots)

                # Penalize if next slot is invalid or doesn't match the sequence
                if (
                    next_slot is None
                    or allotable.next_slot_allotable.id != next_slot.slot_alloted_to.id
                    or allotable.continuous_left != next_slot.slot_alloted_to.continuous_left + 1

                ):
                    slot.penalty += allotable.continuous_left

                    total_penalty += allotable.continuous_left

            # Case 2: Last allotable in the sequence (no next_slot_allotable)
            elif allotable.allotable_entity.continuous_slot > 1:
                previous_slot = get_previous_slot(slot=slot, university_slots=university_slots)

                # Penalize if no previous slot or sequence mismatch
                if (
                    previous_slot is None
                    or previous_slot.slot_alloted_to.next_slot_allotable is None
                    or previous_slot.slot_alloted_to.next_slot_allotable.id != allotable.id
                    or allotable.continuous_left != previous_slot.slot_alloted_to.continuous_left - 1
                ):
                #     slot.penalty += allotable.allotable_entity.continuous_slot - 1
                    
                #     total_penalty += allotable.allotable_entity.continuous_slot - 1



                # previous_slot = get_previous_slot(slot=slot, university_slots=university_slots)

                # if (
                #     previous_slot is None
                #     or previous_slot.slot_alloted_to.next_slot_allotable != slot.slot_alloted_to.previous_slot_allotable
                # ):
                    slot.penalty += allotable.continuous_left

                    total_penalty += allotable.continuous_left
        return self.penalty * total_penalty





    def is_correct_next_continuous_slot(self,slot_allotable_1:SlotAllotable,slot_allotable_2:SlotAllotable):
        # if slot_allotable_2.allotable_entity.type !='TeachingEntity':
        #     return False
        if slot_allotable_1.allotable_entity.id != slot_allotable_2.allotable_entity.id or slot_allotable_1.continuous_left != slot_allotable_2.continuous_left +1 or slot_allotable_2.continuous_left == 1:
        # if slot_allotable_1.allotable_entity.id != slot_allotable_2.allotable_entity.id or slot_allotable_1.continuous_left != slot_allotable_2.continuous_left +1:

            return False
        return True

    def is_non_continuous_slot(self,slot_allotable_1:SlotAllotable,slot_allotable_2:SlotAllotable):
        # if slot_allotable_2.allotable_entity.type !='TeachingEntity':
        #     return False
        if slot_allotable_1.allotable_entity.id != slot_allotable_2.allotable_entity.id and  slot_allotable_1.continuous_left != slot_allotable_2.continuous_left +1:
        # if slot_allotable_1.allotable_entity.id != slot_allotable_2.allotable_entity.id or slot_allotable_1.continuous_left != slot_allotable_2.continuous_left +1:

            return False
        return True

    def _get_next_correct_allotable(self,slot_allotable:SlotAllotable):
        data_pool_allotables:List[SlotAllotable] = self.generic.data_pool.allotables
        for allotable in data_pool_allotables:
            if allotable.allotable_entity.id == slot_allotable.allotable_entity.id and slot_allotable.continuous_left == allotable.continuous_left +1:
                 return allotable
        return None

    def _get_safe_allotable(self,slot):
        valid_gene = True
        new_gene:Slot = None
        while valid_gene != False:
            new_gene = self.generic.gene_generator(mutation_mode=True)
            valid_gene = self.is_correct_next_continuous_slot(slot.slot_alloted_to, new_gene.slot_alloted_to)
        return new_gene



    # def repair_chromosome(self, chromosome: Chromosome):
    #     total_penalty = 0
    #     university_slots: List[Slot] = chromosome.genes

    #     for slot in university_slots:
    #         # allotable = slot.slot_alloted_to

    #         # Case 1: There is a next_slot_allotable
    #         if slot.slot_alloted_to.next_slot_allotable is not None:
    #             next_slot = get_next_slot(slot=slot, university_slots=university_slots)

    #             # Penalize if next slot is invalid or doesn't match the sequence
    #             if (
    #                 next_slot is None
    #                 or slot.slot_alloted_to.next_slot_allotable.id != next_slot.slot_alloted_to.id
    #                 or slot.slot_alloted_to.continuous_left != next_slot.slot_alloted_to.continuous_left + 1
    #             ):
    #                 if next_slot is None:


    #                     # slot.slot_alloted_to = self._get_safe_allotable(slot=slot).slot_alloted_to
    #                     pass

    #                 else:
    #                     next_slot_allotable = self._get_next_correct_allotable(slot_allotable=slot.slot_alloted_to)
    #                     if next_slot_allotable is not None:
    #                         slot_for_the_allotable = get_current_slot_from_allotable(next_slot_allotable, university_slots=university_slots)
    #                         slot_for_the_allotable.slot_alloted_to = slot.slot_alloted_to.next_slot_allotable
    #                         slot.slot_alloted_to.next_slot_allotable = next_slot_allotable
    #                     else:
    #                         pass

    #         # Case 2: Last allotable in the sequence (no next_slot_allotable)
    #         elif slot.slot_alloted_to.allotable_entity.continuous_slot > 1:
    #             previous_slot = get_previous_slot(slot=slot, university_slots=university_slots)

    #             # Penalize if no previous slot or sequence mismatch
    #             if (
    #                 previous_slot is None
    #                 or previous_slot.slot_alloted_to.next_slot_allotable is None
    #                 or previous_slot.slot_alloted_to.next_slot_allotable.id != slot.slot_alloted_to.id
    #                 or slot.slot_alloted_to.continuous_left != previous_slot.slot_alloted_to.continuous_left - 1
    #             ):
    #                 if previous_slot is None or previous_slot.slot_alloted_to.next_slot_allotable is None:
    #                     slot.slot_alloted_to = self._get_safe_allotable(slot=slot).slot_alloted_to
    #                 else:
    #                     slot.slot_alloted_to = self._get_safe_allotable(slot=slot).slot_alloted_to

    #     chromosome.genes = university_slots

    #     return chromosome


    def repair_chromosome(self, chromosome: Chromosome):
        return chromosome



class AllAllotablesAssignedConstraint(Constraint):

    def apply_constraint(self, chromosome: Chromosome):
        total_penalty = 0
        assigned_allotables = {slot.slot_alloted_to.id for slot in chromosome.genes}
        for allotable in self.generic.data_pool.allotables:
            if allotable.id not in assigned_allotables:
                
                total_penalty += 1
        
        return self.penalty * total_penalty

    def repair_chromosome(self, chromosome):   
        return chromosome


class NoAllotableRepetitionConstraint(Constraint):
    def apply_constraint(self, chromosome: Chromosome):
        total_penalty = 0
        allotables = defaultdict(int)

        for slot in chromosome.genes:
            if slot.slot_alloted_to:
                allotables[slot.slot_alloted_to.id] += 1

        for count in allotables.values():
            total_penalty += max(count - 1, 0)

        return self.penalty * total_penalty


    def repair_chromosome(self, chromosome):   
        return chromosome



class AllotableCorrectDivision(Constraint):

    def apply_constraint(self, chromosome):
        total_penalty = 0
        slots:List[Slot] = chromosome.genes

        for slot in slots:
            if slot.slot_alloted_to.allotable_entity.type != 'EmptyEntity':
                if slot.slot_alloted_to.allotable_entity.division.id != slot.division.id:
                    slot.penalty+=1
                    total_penalty+=1
        return self.penalty * total_penalty

    def _get_correct_division_allotable(self,slot:Slot):
        while True:
            new_gene : Slot= self.generic.gene_generator()
            if new_gene.slot_alloted_to.allotable_entity.type == 'EmptyEntity':
                return new_gene.slot_alloted_to
            if new_gene.slot_alloted_to.allotable_entity.division.id == slot.division.id:
                return new_gene.slot_alloted_to

    def repair_chromosome(self, chromosome):
        slots:List[Slot] = chromosome.genes

        # for slot in slots:
        #     if slot.slot_alloted_to.allotable_entity.type != 'EmptyEntity':
        #         if slot.slot_alloted_to.allotable_entity.division.id != slot.division.id:
        #             slot.slot_alloted_to = self._get_correct_division_allotable(slot=slot)

        # chromosome.genes = slots
        return chromosome
# # ---------------------------------------------


   
