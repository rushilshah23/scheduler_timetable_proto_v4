from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Callable

import random

@dataclass
class DataPool:
    pass


@dataclass
class Gene:
    pass
    def to_dict(self):
        return super().to_dict()


@dataclass
class Chromosome:
    genes: List[Gene] = field(default_factory=list)
    fitness:float=0.0

    def to_dict(self):
        return {
            "genes":[gene.to_dict() for gene in self.genes]
        }


@dataclass
class Constraint(ABC):
    penalty:float
    generic:'GeneticAlgorithmFunctionalities'
    type:str='HARD'

    @abstractmethod
    def apply_constraint(self, chromosome:Chromosome)->float:
        pass
    
    @abstractmethod
    def repair_chromosome(self, chromosome:Chromosome)->Chromosome:
        # return chromosome
        pass

@dataclass
class FitnessEvaluator:
    max_score:float
    
    constraints:List[Constraint] = field(default_factory=list)


    def evaluate_fitness(self, chromosome:Chromosome, only_hard_mode=False)->int:
        total_penalty = 0.0
        for constraint in self.constraints:
            if (only_hard_mode == True and constraint.type == 'HARD') or only_hard_mode == False:
                penalty = constraint.apply_constraint(chromosome=chromosome)
                total_penalty+=penalty
        # print("Max score ",self.max_score)
        return max(0, self.max_score-total_penalty)
    
    def repair_chromosome(self, chromosome:Chromosome)->Chromosome:
        for constraint in self.constraints:
            chromosome =  constraint.repair_chromosome(chromosome=chromosome)
        return chromosome


@dataclass
class DNA:
    chromosomes:List[Chromosome] = field(default_factory=list)

@dataclass
class GeneticAlgorithmConfig:
    MAX_GENERATION:int
    DNA_SIZE:int
    MUTATION_RATE:float
    REPAIR_MODE:bool = False
    # MAX_STAGNATION:int
    
@dataclass
class GeneticAlgorithmFunctionalities:
    data_pool:DataPool
    CHROMOSOME_LENGTH:int

    @abstractmethod
    def chromosome_generator(self)->Chromosome:
        pass
    @abstractmethod
    def gene_generator(self)->Gene:
        pass
    @abstractmethod
    def mutator(self,chromosome:Chromosome)->Chromosome:
        pass

@dataclass
class GeneticAlgorithmMachine():
    fitness_evaluator:FitnessEvaluator
    generics:GeneticAlgorithmFunctionalities

    ga_config:GeneticAlgorithmConfig
    population:DNA = None

    def __post_init__(self):
        self.population = DNA()

    def generate_initial_DNA(self)->List[Chromosome]:
        count = 0
        while len(self.population.chromosomes) < self.ga_config.DNA_SIZE:
            new_chromosome = self.generics.chromosome_generator()
            new_chromosome = self.fitness_evaluator.repair_chromosome(new_chromosome)
            new_chromosome.fitness = self.fitness_evaluator.evaluate_fitness(new_chromosome, only_hard_mode=True)
            # print(f"Total initial fitness = {new_chromosome.fitness}")
            if new_chromosome.fitness >= self.fitness_evaluator.max_score* 0.9:
                count+=1
                print(f"Chromosome generated - {count}\t Fitness = {new_chromosome.fitness}")
                # print("FItness  - ",new_chromosome.fitness)
                self.population.chromosomes.append(new_chromosome)
        # print("Initial Population")
        # import time
        # time.sleep(2)

    def evaluate_DNA(self):
        for chromosome in self.population.chromosomes:
            chromosome.fitness = self.fitness_evaluator.evaluate_fitness(chromosome)

    def repair_DNA(self):
        for i, chromosome in enumerate(self.population.chromosomes):
            self.population.chromosomes[i] = self.fitness_evaluator.repair_chromosome(chromosome)


    def tournament_selection(self, tournament_size: int = 10) -> Chromosome:
        tournament = random.sample(self.population.chromosomes, tournament_size)
        tournament.sort(key=lambda c: c.fitness, reverse=True)
        return tournament[0]
    

    def select_parents(self):
        parent1 = self.tournament_selection(max(10,int(self.ga_config.DNA_SIZE/4)))
        parent2 = self.tournament_selection(max(10,int(self.ga_config.DNA_SIZE/4)))
        return parent1, parent2
    
        # self.population.chromosomes.sort(key=lambda c: c.fitness, reverse=True)
        # return self.population.chromosomes[:2]  # Top two chromosomes as parents



    def crossover(self, parent_1: Chromosome, parent_2: Chromosome) -> Chromosome:
        # crossover_point = random.randint(0, len(parent_1.genes) - 1)
        # new_genes = parent_1.genes[:crossover_point] + [gene for gene in parent_2.genes if gene not in parent_1.genes[:crossover_point]]
        crossover_point1 = random.randint(0, len(parent_1.genes) - 1)
        crossover_point2 = random.randint(crossover_point1, len(parent_1.genes) - 1)
        new_genes = parent_1.genes[:crossover_point1] + parent_2.genes[crossover_point1:crossover_point2] + parent_1.genes[crossover_point2:]
        child = Chromosome(genes=new_genes)
        return child
        return self.fitness_evaluator.repair_chromosome(child)  # Apply repair after crossover
    
    # def crossover(self, parent_1: Chromosome, parent_2: Chromosome) -> Chromosome:
        # Determine the number of crossover points based on chromosome size
        num_crossover_points = max(2, len(parent_1.genes) // 5)  # At least 2 crossover points, scaled by size
        crossover_points = sorted(random.sample(range(len(parent_1.genes)), num_crossover_points))
        
        # Alternate segments between parents
        new_genes = []
        use_parent_1 = True
        start_idx = 0
        
        for cp in crossover_points:
            if use_parent_1:
                new_genes.extend(parent_1.genes[start_idx:cp])
            else:
                new_genes.extend(parent_2.genes[start_idx:cp])
            start_idx = cp
            use_parent_1 = not use_parent_1
        
        # Append the remaining segment
        if use_parent_1:
            new_genes.extend(parent_1.genes[start_idx:])
        else:
            new_genes.extend(parent_2.genes[start_idx:])
        
        # Remove duplicates manually using a list
        unique_genes = []
        for gene in new_genes:
            if gene not in unique_genes:  # Manual duplicate check
                unique_genes.append(gene)
        
        # Create and return the child chromosome
        child = Chromosome(genes=unique_genes)
        return child


    def mutate(self,chromosome:Chromosome,mutation_rate:float)->Chromosome:
        for i, gene in enumerate(chromosome.genes):
            if random.random() < mutation_rate:
                chromosome = self.generics.mutator(chromosome=chromosome) 
        # return self.fitness_evaluator.repair_chromosome(chromosome)
        return chromosome

    from src_v4.utils.generic_utils import timer
    # @timer
    def perform_ga(self)->Chromosome:
        try:
            
            self.generate_initial_DNA()

            generation_count = 0
            while generation_count < self.ga_config.MAX_GENERATION:
                if self.ga_config.REPAIR_MODE == True:
                    self.repair_DNA()
                self.evaluate_DNA()
                parent_1,parent_2 = self.select_parents()
                child = self.crossover(parent_1=parent_1, parent_2=parent_2)

                child = self.mutate(chromosome=child,mutation_rate=self.ga_config.MUTATION_RATE)
                if self.ga_config.REPAIR_MODE == True:
                    child = self.fitness_evaluator.repair_chromosome(child)
                # child = self.fitness_evaluator.repair_chromosome(child)

                child.fitness = self.fitness_evaluator.evaluate_fitness(child)
                self.population.chromosomes.sort(key=lambda chromosome:chromosome.fitness, reverse=True)
                if child.fitness >= self.population.chromosomes[-1].fitness:
                    self.population.chromosomes[-1] = child
                self.population.chromosomes.sort(key=lambda chromosome:chromosome.fitness, reverse=True)

                generation_count+=1
                if generation_count%(self.ga_config.MAX_GENERATION/100) == 0:

                    print(f"Generation - {generation_count}\tbest fitness = {self.population.chromosomes[0].fitness}\tworst fitness = {self.population.chromosomes[-1].fitness}\tMax Fitness = {self.fitness_evaluator.max_score}")
                    # print(self.population.chromosomes[0].genes)
                    pass
                if self.population.chromosomes[0].fitness == self.fitness_evaluator.max_score:
                    # print("Best chromosme achieved !")

                    # print(f"Generation - {generation_count}\tbest fitness = {self.population.chromosomes[0].fitness}\tworst fitness = {self.population.chromosomes[-1].fitness}\tMax Fitness = {self.fitness_evaluator.max_score}")
                    return self.population.chromosomes[0]
            print("INcomplete solution but still .... ")

            return self.population.chromosomes[0]
        except KeyboardInterrupt as e:
            return self.population.chromosomes[0]
        