from dataclasses import dataclass
from typing import List, Dict, Union, Literal
from src_v5.ga import Chromosome,Constraint,DataPool,FitnessEvaluator,GeneticAlgorithmConfig,GeneticAlgorithmMachine,GeneticAlgorithmFunctionalities
from src_v5.domain.university import *
import random
import copy
from src_v5.utils.generic_utils import timer
from src_v5.utils.generic_utils import get_new_id
from src_v5.utils.business_utils import *
from src_v5.constraints import *


@dataclass
class SlotData:
    slots:List[Slot]
    allotables:List[SlotAllotable]

@dataclass
class UniversityTimetablerGeneticAlgorithmMachine(GeneticAlgorithmMachine):
    def _group_by_division(self,slots: List[Slot]) -> Dict[str, List[Slot]]:
        division_slots = {}
        for slot in slots:
            div_id = slot.division.id
            division_slots.setdefault(div_id, []).append(slot)
        return division_slots

    def crossover(self, parent_1: Chromosome, parent_2: Chromosome) -> Chromosome:
        parent_1_div_slots = self._group_by_division(parent_1.genes)
        parent_2_div_slots = self._group_by_division(parent_2.genes)

        child_slots = []
        common_divisions = set(parent_1_div_slots.keys()).intersection(parent_2_div_slots.keys())

        for div_id in common_divisions:
            slots_1 = parent_1_div_slots[div_id]
            slots_2 = parent_2_div_slots[div_id]

            # print(f"Division ID: {div_id}, Parent 1 Slot Count: {len(slots_1)}, Parent 2 Slot Count: {len(slots_2)}")


            if len(slots_1) != len(slots_2):
                print(f"{len(slots_1)} and {len(slots_2)}")
                raise ValueError(f"Mismatch in slot counts for division {div_id}")

            for slot_1, slot_2 in zip(slots_1, slots_2):
                new_slot = copy.deepcopy(slot_1)
                if random.random() > 0.5:
                    new_slot.slot_alloted_to = slot_2.slot_alloted_to
                child_slots.append(new_slot)

        return Chromosome(genes=child_slots)



@dataclass
class TimetableGenerics(GeneticAlgorithmFunctionalities):
    data_pool:SlotData
    # semi_fitness_evaluator:FitnessEvaluator
    def __post_init__(self):
        self.editable_data_pool = copy.deepcopy(self.data_pool)

    # def gene_level_validation(self,slot:Slot, allotable:SlotAllotable):

    #     valid_gene = True
    #     if allotable.allotable_entity.type != 'EmptyEntity':
    #         if slot.division.id != allotable.allotable_entity.division.id:
    #             valid_gene = False
    #     return valid_gene


    def _slot_and_allotable_same_division(self,slot:Slot, allotable:SlotAllotable):
        return allotable.allotable_entity.division.id == slot.division.id
   
    def _remove_slot_and_allotable_in_editable_pool(self,gene:Slot):
        slot_removed, allotable_removed = False

        for slot in self.editable_data_pool.slots:
            if slot.id == gene.id:
                for allotable in self.editable_data_pool.allotables:
                    if allotable.id == gene.slot_alloted_to.id: 
                        self.editable_data_pool.allotables.remove(allotable)
                        allotable_removed = True
                self.editable_data_pool.slots.remove(slot)
                slot_removed = True
        if slot_removed == False:
            raise Exception(f"Slot missing to be removed in editable pool")
        if allotable_removed == False:
            raise Exception(f"Allotable missing to be removed in editable pool")



    def gene_generator(self,mutation_mode=False)->Gene:
        # print(f"{len(self.editable_data_pool.slots)} and {len(self.editable_data_pool.allotables)}")
        if len(self.editable_data_pool.slots) == 0 and len(self.editable_data_pool.allotables) == 0:
            self.editable_data_pool = copy.deepcopy(self.data_pool)
        if mutation_mode == True:
            allotables = self.data_pool.allotables
            slots = self.data_pool.slots
        else:
            allotables:List[SlotAllotable] = self.editable_data_pool.allotables
            slots:List[Slot] = self.editable_data_pool.slots

        gene = None
        # valid_gene = False
        # while valid_gene != True:
        random_slot = None
        random_allotable = None
        while True:
            random_allotable = random.choice(allotables)
            random_slot =  random.choice(slots)
            if random_allotable.allotable_entity.type == "EmptyEntity":
                non_empty_entity_exists = False
                for allotable in allotables:
                    if allotable.allotable_entity.type != "EmptyEntity":
                        non_empty_entity_exists = True
                if non_empty_entity_exists == False:
                    break
            elif self._slot_and_allotable_same_division(slot=random_slot, allotable=random_allotable) ==  True:
                break
            # valid_gene = self.gene_level_validation(slot=random_slot, allotable=random_allotable)

        gene = random_slot
        gene.slot_alloted_to = random_allotable
        return gene





    def chromosome_generator(self)->Chromosome:
        chromosome:Chromosome = Chromosome()
        for i in range(0, self.CHROMOSOME_LENGTH):
            correct_gene = False
            while correct_gene is False:
                # print(f"slots =  {len(self.editable_data_pool.slots)}\tALlotables = {len(self.editable_data_pool.allotables)}")
                gene = self.gene_generator()
                
                if gene not in chromosome.genes:
                    # if self.semi_fitness_evaluator.evaluate_fitness(chromosome) == self.semi_fitness_evaluator.max_score:
                    for slot in self.editable_data_pool.slots:
                        if slot.id == gene.id:
                            for allotable in self.editable_data_pool.allotables:
                                if allotable.id == gene.slot_alloted_to.id: 
                                    self.editable_data_pool.allotables.remove(allotable)
                            self.editable_data_pool.slots.remove(slot)

                    correct_gene = True
                    chromosome.genes.append(gene)
                else:
                    # chromosome.genes.pop()
                    pass
        return chromosome


    def mutator(self,chromosome:Chromosome)->Chromosome:

        mutation_index = random.randint(0, len(chromosome.genes) - 1)
        chromosome.genes[mutation_index].slot_alloted_to = self.gene_generator(mutation_mode=True).slot_alloted_to

        # chromosome = self.chromosome_generator()
        return chromosome
         


def create_chromosome(slots:List[Slot]=None, allotables:List[SlotAllotable]=None,data_pool:DataPool=None)->Chromosome:

    # print(f"Total slots count  = {len(data_pool.slots)}\tTotal allotables count = {len(data_pool.allotables)}")

    CHROMOSOME_LENGTH = len(slots) 

    generics = TimetableGenerics(
        CHROMOSOME_LENGTH=CHROMOSOME_LENGTH,
        data_pool=data_pool
    )



    fitness_evaluator = FitnessEvaluator(
        max_score=CHROMOSOME_LENGTH * 2,
        constraints=[
            NoSlotRepeatedSlotConstraint(1,type='HARD', generic=generics ),
            NoFacultyOverlapConstraint(1,type='HARD', generic=generics ),
            ContinuousSlotConstraint(1,type='HARD', generic=generics ),
            AllAllotablesAssignedConstraint(1,type='HARD', generic=generics ),
            NoAllotableRepetitionConstraint(1,type='HARD', generic=generics ),
            AllotableCorrectDivision(1,type='HARD', generic=generics ),

        ]
    )

    ga_config = GeneticAlgorithmConfig(
        MAX_GENERATION=2000,
        DNA_SIZE=1000,
        MUTATION_RATE=0.08,
        REPAIR_MODE=True
    )

    # timetable_generator = GeneticAlgorithmMachine(
    #     fitness_evaluator=fitness_evaluator,
    #     generics=generics,
    #     ga_config=ga_config
    # )

    timetable_generator = UniversityTimetablerGeneticAlgorithmMachine(
        fitness_evaluator=fitness_evaluator,
        generics=generics,
        ga_config=ga_config
    )
    # Add genes to semi_chromosome until it reaches max_score
    counter = 0
    # while counter < 10:
    while True:
        chromosome = timetable_generator.perform_ga()

        temp_semi_chromosome = fitness_evaluator.repair_chromosome(chromosome)
        current_score = fitness_evaluator.evaluate_fitness(chromosome)
        print(f"Current Fitness score  = {current_score}\tMaximum fitness score = {fitness_evaluator.max_score}")
        if current_score == fitness_evaluator.max_score:
            chromosome = temp_semi_chromosome
            return chromosome
    #     counter+=1
    #     semi_chromosome = temp_semi_chromosome
    # return semi_chromosome




@timer
def generate_timetable(parsed_data):


    data_pool:SlotData = SlotData(
        slots=parsed_data["slots"],
        allotables=parsed_data['allotables']
    )
    # print(f"Before empty - len of allotbales = {len(data_pool.allotables)}")
    if len(data_pool.allotables) < len(data_pool.slots):
        for i in range((len(data_pool.slots) - len(data_pool.allotables))): 
            empty_entity = EmptyEntity(id=get_new_id(), continuous_slot=1, maximum_weekly_frequency=1)
            new_slot_allotable = SlotAllotable(id=get_new_id(), allotable_entity=empty_entity,next_slot_allotable=None, continuous_left=1)
            data_pool.allotables.append(new_slot_allotable)

    final_chromosome = create_chromosome(slots=data_pool.slots, allotables=data_pool.allotables, data_pool=data_pool)


    return final_chromosome