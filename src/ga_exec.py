from dataclasses import dataclass
from typing import List, Dict, Union, Literal
from src.ga import *
from src.domain import *

@dataclass
class SlotData:
    slots:List[Slot]
    allotables:List[SlotAllotable]