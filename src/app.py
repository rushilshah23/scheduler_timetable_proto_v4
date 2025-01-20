import json
from src.data_validation import validate_stage_1
from src.business_validation import validate_stage_2
from src.transformer import transform
if __name__ == "src.app":

    with open("./data/inputs/input_1.json","r") as input_data:
        input_data = json.load(input_data)
        validate_stage_1(input_data=input_data)
        validate_stage_2(input_data=input_data)

        input_data = transform(input_data= input_data)
        from src.utils.generic_utils import save_output_file
        save_output_file('output_1.json',input_data)
