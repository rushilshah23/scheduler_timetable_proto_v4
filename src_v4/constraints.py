from src_v4.ga import Constraint, Chromosome

class NoSameSlotRepeated(Constraint):
    def apply_constraint(self, chromosome:Chromosome):
        total_penalty = 0
        slots = chromosome.genes
        slot_dict = {}
        for slot in slots:
            if slot.id in slot_dict:
                slot_dict[slot.id]+=1
            else:
                slot_dict[slot.id] = 1
        for slot_id, count in slot_dict.items():
            total_penalty+=max(0, count-1)
        return self.penalty * total_penalty
    
        