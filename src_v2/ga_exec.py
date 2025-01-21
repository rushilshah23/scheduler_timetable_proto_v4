from dataclasses import dataclass
from typing import List, Dict, Union, Literal
from src_v2.ga import *
from src_v2.domain import *
import random
import copy
from src_v2.utils.generic_utils import timer
from src_v2.utils.generic_utils import get_new_id
from src_v2.utils.business_utils import *

@dataclass
class SlotData:
    slots:List[Slot]
    allotables:List[SlotAllotable]


def slot_generator():
    pass

def slots_generator(parsed_data):
    slots : List[Slot] = []

    for division in parsed_data['divisions']:
        working_days_for_division = next((working_day for working_day in parsed_data['working_days'] if working_day['division_id'] == division.id),None )
    for working_day in working_days_for_division:
        weekly_slot_count = 0
        slots_timings_for_working_day = get_timings_wrt_slotsize(working_day.start_time, working_day.end_time, working_day.slot_duration)
        daily_slot_count = 0
        for timings in slots_timings_for_working_day:    
            slot = Slot(
                id = get_new_id(),
                start_time=timings['start_time'],
                end_time = timings['end_time'],
                working_day=working_day,
                working_day_id=working_day.id,
                daily_slot_number=daily_slot_count,
                weekly_slot_number=weekly_slot_count,
                slot_alloted_to_allotable=None,
                slot_alloted_to_allotable_id=None
            )
            daily_slot_count+=1
            weekly_slot_count+=1
            slots.append(slot)
    return slots

def allotable_generator():
    pass

def allotables_generator(parsed_data):
    allotables : List[SlotAllotable] = []

    for allotable in parsed_data['slot_allotables']:


        slot_allotable = SlotAllotable(
            allotable_entity=allotable["allotable_entity"],
            allotable_entity_id=allotable["allotable_entity_id"],
            start_time_rule=allotable['start_time_rule'],
            end_time_rule=allotable['end_time_rule'],
            continuous_slot_rule=allotable['continuous_slot_rule'],
            division= allotable['division'],
            division_id=allotable['division_id'],
            id=get_new_id(),
            maximum_daily_frequency_rule=allotable['maximum_daily_frequency_rule'],
            maximum_weekly_frequency_rule=allotable['maximum_weekly_frequency_rule'],
            minimum_daily_frequency_rule=allotable['minimum_daily_frequency_rule'],
            minimum_weekly_frequency_rule=allotable['minimum_weekly_frequency_rule'],
            next_slot_allotable=None,
            next_slot_allotable_id=None,
            working_day=allotable['working_day'],
            working_day_id=allotable['working_day_id'],
            working_day_rule=allotable['working_day_rule'],
        )
        max_weekly_count = int(allotable['maximum_weekly_frequency_rule']['max_weekly_frequency'])
        continuous_slot = int(allotable['continuous_slot_rule'][''])
        
        for _ in range(max_weekly_count/continuous_slot):
            pass
            # CONTINUE FROM HERE 




@dataclass
class TimetableGenerics(GeneticAlgorithmFunctionalities):
    data_pool:SlotData
    # semi_fitness_evaluator:FitnessEvaluator

    def gene_generator(self)->Gene:

        allotables = self.data_pool.allotables
        slots = self.data_pool.slots
        if len(self.data_pool.allotables) < len(self.data_pool.slots):
            allotables.extend([None] * (len(slots) - len(allotables)))
        random_allotable = random.choice(allotables)
        random_slot =  random.choice(slots)
        gene = random_slot
        gene.slot_alloted_to = random_allotable
        return gene

    def chromosome_generator(self)->Chromosome:
        chromosome:Chromosome = Chromosome()
        for i in range(0, self.CHROMOSOME_LENGTH):
            correct_gene = False
            while correct_gene is False:
                gene = self.gene_generator()
                
                if gene not in chromosome.genes:
                    chromosome.genes.append(gene)
                    # if self.semi_fitness_evaluator.evaluate_fitness(chromosome) == self.semi_fitness_evaluator.max_score:
                    correct_gene = True
                else:
                    chromosome.genes.pop()
        return chromosome


    def mutator(self,chromosome:Chromosome)->Chromosome:

        mutation_index = random.randint(0, len(chromosome.genes) - 1)
        chromosome.genes[mutation_index] = self.gene_generator()

        # chromosome = self.chromosome_generator()
        return chromosome
         


def create_semi_chromosome(slots:List[Slot]=None, allotables:List[SlotAllotable]=None,semi_chromosome:Chromosome=None, global_data_pool:DataPool=None, university_data_pool:DataPool=None)->Chromosome:
    current_data_pool = SlotData(
        slots=slots,
        allotables=allotables
    )


    CHROMOSOME_LENGTH = len(semi_chromosome.genes) + 1
    generics = TimetableGenerics(
        CHROMOSOME_LENGTH=CHROMOSOME_LENGTH,
        data_pool=current_data_pool
    )

    semi_chromosome_generics = TimetableGenerics(
        CHROMOSOME_LENGTH=CHROMOSOME_LENGTH,
        # data_pool=global_data_pool
        data_pool=current_data_pool

    )

    fitness_evaluator = FitnessEvaluator(
        max_score=CHROMOSOME_LENGTH * 2,
        constraints=[
            IncompleteSlots(5, data_pool=current_data_pool, type='HARD', generic=generics),
            NoSameSlotIdRepetition(1 / 2, data_pool=current_data_pool, type='HARD', generic=generics),
            # AllAllotablesMapped(1, data_pool=current_data_pool, type='HARD', generic=generics),
            # DuplicateAllotables(1, data_pool=current_data_pool, type='HARD', generic=generics),

            FixedAllotablesAtFixedSlot(2, data_pool=current_data_pool, type='HARD', generic=generics)
        ]
    )

    semi_chromosome_fitness_evaluator = FitnessEvaluator(
        max_score=CHROMOSOME_LENGTH * 2,
        constraints=[
            IncompleteSlots(5, data_pool=global_data_pool, type='HARD', generic=semi_chromosome_generics),
            NoSameSlotIdRepetition(1 / 2, data_pool=global_data_pool, type='HARD', generic=semi_chromosome_generics),
            # AllAllotablesMapped(1, data_pool=current_data_pool, type='HARD', generic=semi_chromosome_generics),
            FixedAllotablesAtFixedSlot(2, data_pool=global_data_pool, type='HARD', generic=semi_chromosome_generics),
            DuplicateAllotables(1, data_pool=global_data_pool, type='HARD', generic=generics),
            MissingAllotables(1, data_pool=university_data_pool, type='HARD', generic=generics),
            ContinuousSlot(1, data_pool=university_data_pool, type='HARD', generic=generics),


        ]
    )

    final_chromosome_fitness_evaluator = FitnessEvaluator(
        max_score=CHROMOSOME_LENGTH * 2,
        constraints=[
            IncompleteSlots(5, data_pool=university_data_pool, type='HARD', generic=semi_chromosome_generics),
            NoSameSlotIdRepetition(1 / 2, data_pool=university_data_pool, type='HARD', generic=semi_chromosome_generics),
            # AllAllotablesMapped(1, data_pool=current_data_pool, type='HARD', generic=semi_chromosome_generics),
            FixedAllotablesAtFixedSlot(2, data_pool=university_data_pool, type='HARD', generic=semi_chromosome_generics),
            DuplicateAllotables(1, data_pool=university_data_pool, type='HARD', generic=generics),
            MissingAllotables(1, data_pool=university_data_pool, type='HARD', generic=generics),
            ContinuousSlot(1, data_pool=university_data_pool, type='HARD', generic=generics),


        ]
    )

    ga_config = GeneticAlgorithmConfig(
        MAX_GENERATION=1000,
        DNA_SIZE=500,
        MUTATION_RATE=0.05,
        REPAIR_MODE=False
    )

    timetable_generator = GeneticAlgorithmMachine(
        fitness_evaluator=fitness_evaluator,
        generics=generics,
        ga_config=ga_config
    )

    # Add genes to semi_chromosome until it reaches max_score
    counter = 0
    # while counter < 10:
    while True:
        new_genes = timetable_generator.perform_ga().genes
        temp_semi_chromosome = copy.deepcopy(semi_chromosome)
        temp_semi_chromosome.genes.extend(new_genes)
        temp_semi_chromosome = semi_chromosome_fitness_evaluator.repair_chromosome(temp_semi_chromosome)
        current_score = semi_chromosome_fitness_evaluator.evaluate_fitness(temp_semi_chromosome)

        if len(temp_semi_chromosome.genes) == len(university_data_pool.slots):
            print("Evaluating final chromsome !")
            temp_semi_chromosome = final_chromosome_fitness_evaluator.repair_chromosome(temp_semi_chromosome)
            current_score = final_chromosome_fitness_evaluator.evaluate_fitness(temp_semi_chromosome)
            print(f"CUrrent final score = {current_score}")
        print(f"LEngth- {len(semi_chromosome.genes)}\tCurrent score - {current_score}\tMax score - {semi_chromosome_fitness_evaluator.max_score}")
        if current_score == semi_chromosome_fitness_evaluator.max_score:
            semi_chromosome = temp_semi_chromosome
            return semi_chromosome
    #     counter+=1
    #     semi_chromosome = temp_semi_chromosome
    # return semi_chromosome


@timer
def generate_timetable(parsed_data):

    final_chromosome = Chromosome(genes=[])

    university = parsed_data['university']
    for working_day in parsed_data['working_days']:
        slots = slots_generator(parsed_data=parsed_data,university_id=university["id"])
        slot_allotables = allotables_generator(parsed_data=parsed_data,university_id=university["id"])



    return final_chromosome