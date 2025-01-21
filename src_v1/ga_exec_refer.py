from src.ga import Gene, Chromosome, DNA,FitnessEvaluator,GeneticAlgorithmFunctionalities,GeneticAlgorithmMachine, DataPool, GeneticAlgorithmConfig
from dataclasses import dataclass
import random
from typing import List


from src.domain import * 
from src.modules.constraints import NoSameSlotIdRepetition,FixedAllotablesAtFixedSlot,IncompleteSlots,DuplicateAllotables, MissingAllotables, ContinuousSlot

import json
from src.business.input_parser import parse_input_json_to_python
from src.business.domain_utils import DomainUtils
from src.business.business_utils import Utils
from src.business.utils import save_output_file
from src.utils.timer import timer
import copy


@dataclass
class SlotData(DataPool):
    allotables: List[SlotAllotable]
    slots: List[Slot]

    def __post_init__(self):
        if len(self.allotables) > len(self.slots):
            while len(self.allotables) < len(self.slots):
                self.allotables.append(None)

                

def slots_generator( working_day_id=None, division_id=None, standard_id=None, department_id=None, university_id=None):
    slots:List[Slot] = []
    # if slot_id is not None:
    #     slots.extend(Utils.cr(working_day_id=working_day_id))
    if working_day_id is not None:
        slots.extend(Utils.create_working_day_slots_table(working_day_id=working_day_id))
    elif division_id is not None:
        slots.extend(Utils.create_division_slots_table(division_id=division_id))
    elif standard_id is not None:
        slots.extend(Utils.create_standard_slots_table(standard_id=standard_id))
    elif department_id is not None:
        slots.extend(Utils.create_department_slots_table(department_id=department_id))
    elif university_id is not None:
        slots.extend(Utils.create_university_slots_table(university_id=university_id))
    return slots

def slot_allotables_generator(working_day_id=None, division_id=None, standard_id=None, department_id=None, university_id=None):
    allotables:List[SlotAllotable] = []

    if working_day_id is not None:
        working_day:WorkingDay = DomainUtils().get_working_day_from_id(id=working_day_id)
        division_id = working_day.division_id
        probable_allotables_for_working_day = DomainUtils().get_allotables_of_a_division_by_division_id(division_id=division_id)
        allotables.extend(probable_allotables_for_working_day)
    elif division_id is not None:
        probable_allotables_for_division = DomainUtils().get_allotables_of_a_division_by_division_id(division_id=division_id)
        allotables.extend(probable_allotables_for_division)       
    elif standard_id is not None:
        probable_allotables_for_standard = DomainUtils().get_allotables_of_a_standard_by_standard_id(standard_id=standard_id)
        allotables.extend(probable_allotables_for_standard)       
    elif department_id is not None:
        probable_allotables_for_department = DomainUtils().get_allotables_of_a_department_by_department_id(department_id=department_id)
        allotables.extend(probable_allotables_for_department)   
    elif university_id is not None:
        probable_allotables_for_university = DomainUtils().get_allotables_of_a_university_by_university_id(university_id=university_id)
        allotables.extend(probable_allotables_for_university) 
    return allotables


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
def generate_timetable(input_data,university_id:str=None):
    # with open("./timetabler/data/inputs/input_2.json", "r") as f:
    #     input_data = json.load(f)
    
    output = parse_input_json_to_python(input_data)
    DomainUtils(data_source=output)
    # DomainUtils().store_data_in_database(parsed_data=output)
    save_output_file('stage_1_output.json', output)

    index = 0
    final_chromosome = Chromosome(genes=[])
    global_data_pool = SlotData(slots=[], allotables=[])
    university_data_pool = SlotData(slots=[],allotables=[])
    all_allotables = []
    universities = DomainUtils().get_all_universities()
    university = DomainUtils().get_university_by_id(universities[0].id)
    university_slots = slots_generator(university_id=university.id)
    university_allotables = slot_allotables_generator(university_id=university.id)
    university_data_pool.slots = university_slots
    university_data_pool.allotables = university_allotables
    print(len(university_allotables))
    print(university)
    departments = DomainUtils().get_departments_by_university_id(university_id=university.id)

    for department_index, department in enumerate(departments):

        standards = DomainUtils().get_standards_by_department_id(department_id=department.id)
        for standard_index, standard in enumerate(standards):
            divisions = DomainUtils().get_divisions_by_standard_id(standard_id=standard.id)
            for division_index, division in enumerate(divisions):
                allotables = slot_allotables_generator(division_id=division.id)
                # save_output_file('allotables.json',allotables)
                global_data_pool.allotables.extend(allotables)
                all_allotables.extend(allotables)
                working_days = DomainUtils().get_working_days_by_division_id(division_id=division.id)



                for working_day_index, working_day in enumerate(working_days):
                    # print(f"Working day  - {working_day_index}")
                    working_day_id = working_day.id
                    working_day_slots = slots_generator(working_day_id=working_day_id)
                    for working_day_slot in working_day_slots:
                        global_data_pool.slots.append(working_day_slot)
                        index+=1
                        # print(f"INdex - {index}")
                        # final_chromosome.genes.extend(create_semi_chromosome(slots=[working_day_slot], allotables=allotables, semi_chromosome=final_chromosome).genes)
                        final_chromosome = create_semi_chromosome(slots=[working_day_slot], allotables=allotables, semi_chromosome=final_chromosome, global_data_pool=global_data_pool, university_data_pool=university_data_pool)
                        # final_chromosome = create_semi_chromosome(slots=curr_working_day_slots, allotables=allotables, semi_chromosome=final_chromosome)


                        # if index%10 == 0:
                        print(f"Slot - {index} generated!")
                        if index == 80:
                            return final_chromosome
    save_output_file('all_allotables.json', all_allotables)

    return final_chromosome