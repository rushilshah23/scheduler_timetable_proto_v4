from dataclasses import dataclass
from typing import List, Dict, Union, Literal
from src_v4.ga import *
from src_v4.domain import *
import random
import copy
from src_v4.utils.generic_utils import timer
from src_v4.utils.generic_utils import get_new_id
from src_v4.utils.business_utils import *
from src_v4.constraints import *


@dataclass
class SlotData:
    slots:List[Slot]
    allotables:List[SlotAllotable]




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
            NoSameSlotRepeated(1,data_pool=current_data_pool,type='HARD', generic=generics )

        ]
    )

    semi_chromosome_fitness_evaluator = FitnessEvaluator(
        max_score=CHROMOSOME_LENGTH * 2,
        constraints=[
            NoSameSlotRepeated(1,data_pool=global_data_pool,type='HARD', generic=semi_chromosome_generics )


        ]
    )

    final_chromosome_fitness_evaluator = FitnessEvaluator(
        max_score=CHROMOSOME_LENGTH * 2,
        constraints=[

            NoSameSlotRepeated(1,data_pool=university_data_pool,type='HARD', generic=semi_chromosome_generics )


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


def generate_all_slots(parsed_data):
    slots = []
    for division in parsed_data['divisions']:
        weekly_slot_count = 0
        for working_day in parsed_data['working_slots']:
            working_day_id = get_new_id()
            working_day = WorkingDay(
                id=working_day_id,
                day=Day(id=)
            )
            daily_slot_count = 0
            timings = get_timings_wrt_slotsize(working_day['start_time'], working_day['end_time'],working_day['slot_duration'])
            for timing in timings:
                slot = Slot(
                    id=get_new_id(),
                    daily_slot_number=daily_slot_count,
                    weekly_slot_number=weekly_slot_count,
                    end_time=timing['end_time'],
                    start_time=timing['start_time'],
                    slot_alloted_to_allotable=None,
                    slot_alloted_to_allotable_id=None,
                    working_day_id=working_day_id,
                    working_day=

                )
                daily_slot_count+=1
                weekly_slot_count+=1


@timer
def generate_timetable(parsed_data):

    final_chromosome = Chromosome(genes=[])

    master_slots = generate_all_slots(parsed_data)
    data_pool:SlotData = SlotData(
        slots=
    )


    return final_chromosome