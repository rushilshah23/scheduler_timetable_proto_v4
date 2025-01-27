from typing import Dict, Any
import re

def is_valid_time_format(time_str: str) -> bool:
    """
    Validates that the time is in the format '05:00am', '11:00pm', etc.,
    where the hour part always has two digits.
    """
    time_format_regex = r"^(0[1-9]|1[0-2]):[0-5][0-9](am|pm)$"
    return bool(re.match(time_format_regex, time_str))


def validate_constraints(constraints):
    if type(constraints.get("mandatory")) != list:
        raise Exception("Mandatory constraints need to be list")
    else:
        mandatory_constraints = constraints.get("mandatory")
        for constraint in mandatory_constraints:
            if 'name' not in constraint:
                raise Exception("Constraint name should exists for a mandatory constraint")
            if 'value' not in constraint:
                raise Exception("Constraint value should exists for a mandatory constraint")
            if 'value' in constraint:
                if constraint['value'] == 'auto':
                    raise Exception("Mandatory constraints can't have value be auto")
    if type(constraints.get("hard")) != list:
        raise Exception("Hard constraints need to be list")
    else:
        hard_constraints = constraints.get("mandatory")
        for constraint in hard_constraints:
            if 'name' not in constraint:
                raise Exception("Constraint name should exists for a hard constraint")
            if 'value' not in constraint:
                raise Exception("Constraint value should exists for a hard constraint")
            if 'value' in constraint:
                if constraint['value'] == 'auto':
                    raise Exception("HArd constraints can't have value be auto")
    if type(constraints.get("soft")) != list:
        raise Exception("Soft constraints need to be list")
    else:
        soft_constraints = constraints.get("mandatory")
        for constraint in soft_constraints:
            if 'name' not in constraint:
                raise Exception("Constraint name should exists for a soft constraint")
            if 'value' not in constraint:
                raise Exception("Constraint value should exists for a soft constraint")    
            if 'priorityLevel' not in constraint:
                raise Exception("Constraint priorityLevel should exists for a soft constraint")    

def validate_allotables(input_data):
    
    errors = []

    # Validate `allotables`
    allotables = input_data.get("allotables")
    if not allotables:
        errors.append("Allotables are mandatory and must be a non-empty list")
    elif not isinstance(allotables, list):
        errors.append("Allotables must be a list")
    else:
        for idx, allotable in enumerate(allotables):
            if not isinstance(allotable, dict):
                errors.append(f"Allotable at index {idx} must be a dictionary")
                continue

            # Validate `constraints`
            constraints = allotable.get("constraints")
            if not constraints or not isinstance(constraints, list):
                errors.append(f"Allotable at index {idx} must have a 'constraints' field of type list")
            else:
                # Define which keys require integers and which require strings
                int_keys = [
                    'minimumDailyFrequency', 'maximumDailyFrequency',
                    'minimumWeeklyFrequency', 'maximumWeeklyFrequency', 'continuousSlot'
                ]
                time_keys = ['startTime', 'endTime']
                str_keys=['divisionName','dayName']
                for constraint_idx, constraint in enumerate(constraints):
                    for key, val in constraint.items():
                        # Check if the key is an integer-based constraint
                        if key in int_keys:
                            if not (isinstance(val, int) or val == "auto"):
                                errors.append(
                                    f"Constraint key '{key}' at index {constraint_idx} must be an integer or {"auto"}"
                                )
                            int_keys.remove(key)

                        # Check if the key is a string-based constraint
                        elif key in time_keys:
                            if not (isinstance(val, str) or val == "auto" or is_valid_time_format(val) == False ):
                                errors.append(
                                    f"Constraint key '{key}' at index {constraint_idx} must be a string or {"auto"} in corect time format"
                                )
                            time_keys.remove(key)
                        elif key in str_keys:
                            if not (isinstance(val, str) or val == "auto"):
                                errors.append(
                                    f"Constraint key '{key}' at index {constraint_idx} must be a string or {"auto"}"
                                )
                            if key == 'divisionName':
                                if not constraint.get("constraintInformation").get("type") == 'hard':
                                    errors.append(
                                    f"Constraint key '{key}' at index {constraint_idx} must be compuslory have type set as hard"
                                    )
                            str_keys.remove(key)

                        # Validate `constraintInformation`
                        # if key in int_keys + str_keys:
                        constraint_info = constraint.get("constraintInformation")
                        if not isinstance(constraint_info, dict):
                            errors.append(
                                f"'constraintInformation' in constraint key '{key}' at index {constraint_idx} must be a dictionary"
                            )
                        else:

                            if "type" not in constraint_info or constraint_info["type"] not in [
                                "soft", "hard", "auto"
                            ]:
                                errors.append(
                                    f"'type' in 'constraintInformation' of constraint key '{key}' at index {constraint_idx} must be 'soft', 'hard', or 'auto'"
                                )
                            elif constraint_info["type"] == "soft":
                                if "priorityLevel" not in constraint_info or not isinstance(
                                    constraint_info["priorityLevel"], int
                                ):
                                    errors.append(
                                        f"'priorityLevel' in 'constraintInformation' of constraint key '{key}' at index {constraint_idx} must be an integer"
                                    )
                        # else:
                        #     errors.append(f"Key '{key}' is invalid in constraints")
                if len(str_keys) != 0:
                    errors.append(", ".join(str_keys)+" keys are missing for constraint")
                if len(int_keys) != 0:
                    errors.append(", ".join(int_keys)+" keys are missing for constraint")
                if len(time_keys) != 0:
                    errors.append(", ".join(time_keys)+" keys are missing for constraint")
            # Validate `entity`
            entity = allotable.get("entity")
            if not entity or not isinstance(entity, dict):
                errors.append(f"Allotable at index {idx} must have a valid 'entity' dictionary")
            else:
                entity_type = entity.get("type")
                if entity_type == "subjectFacultyDivision":
                    if not isinstance(entity.get("subjectName"), str):
                        errors.append("Entity of type 'subjectFacultyDivision' must have a valid 'subjectName' string")
                    if not isinstance(entity.get("facultyName"), str):
                        errors.append("Entity of type 'subjectFacultyDivision' must have a valid 'facultyName' string")
                    if not isinstance(entity.get("divisionName"), str):
                        errors.append("Entity of type 'subjectFacultyDivision' must have a valid 'divisionName' string")
                elif entity_type == "break":
                    if not isinstance(entity.get("name"), str):
                        errors.append("Entity of type 'break' must have a valid 'name' string")
                elif entity_type == "empty":
                    if entity.get("name") != "empty":
                        errors.append("Entity of type 'empty' must have the name 'empty'")
                else:
                    errors.append(f"Entity type '{entity_type}' is invalid")

            # Validate `preset`
            preset = allotable.get("preset")
            if not preset or not isinstance(preset, list):
                errors.append(f"Allotable at index {idx} must have a 'preset' field of type list")
            else:
                for preset_idx, item in enumerate(preset):
                    if not isinstance(item, dict):
                        errors.append(f"'preset' entry at index {preset_idx} must be a dictionary")
                        continue

                    # Validate `day`
                    day = item.get("day")
                    if not day or not isinstance(day, dict):
                        errors.append(f"'day' in 'preset' entry at index {preset_idx} must be a dictionary")
                    else:
                        if not isinstance(day.get("value"), str):
                            errors.append(f"'value' in 'day' of 'preset' entry at index {preset_idx} must be a string")
                        if not isinstance(day.get("priorityLevel"), int):
                            errors.append(
                                f"'priorityLevel' in 'day' of 'preset' entry at index {preset_idx} must be an integer"
                            )

                        # Validate `startTime` and `endTime`
                        for time_key in ["startTime", "endTime"]:
                            time = day.get(time_key)
                            if not time or not isinstance(time, dict):
                                errors.append(f"'{time_key}' in 'day' of 'preset' entry at index {preset_idx} must be a dictionary")
                            else:
                                if not isinstance(time.get("value"), str or is_valid_time_format(time.get("value")) == False):
                                    errors.append(
                                        f"'value' in '{time_key}' of 'day' in 'preset' entry at index {preset_idx} must be a string"
                                    )
                                if not time.get("constraintInformation") or not isinstance(
                                    time["constraintInformation"], dict
                                ):
                                    errors.append(
                                        f"'constraintInformation' in '{time_key}' of 'day' in 'preset' entry at index {preset_idx} must be a dictionary"
                                    )
                                elif time["constraintInformation"].get("type") not in ["hard", "soft", "auto"]:
                                    errors.append(
                                        f"'type' in 'constraintInformation' of '{time_key}' in 'day' of 'preset' entry at index {preset_idx} must be 'hard', 'soft', or 'auto'"
                                    )
    return errors


# Manually check types for generic collections like List and Dict
def validate_stage_1(input_data: Dict[str, Any]) -> None:
    try:
        errors = []

        # Validate university_name
        university_name = input_data.get("university_name")
        if not university_name:
            errors.append("University name is mandatory")
        elif not isinstance(university_name, str):
            errors.append(f"University name must be a string.")

        # Validate logo
        logo = input_data.get("logo")
        if logo is not None and not isinstance(logo, str):
            errors.append(f"Logo must be a string or None")


        # Validate divisions
        divisions = input_data.get("divisions")
        if not divisions:
            errors.append("Divisions are mandatory and must be a non-empty list")
        elif not isinstance(divisions, list):
            errors.append(f"Divisions must be a list")
        else:
            for idx, division in enumerate(divisions):
                if not isinstance(division, dict):
                    errors.append(f"Division at index {idx} must be a dictionary")
                else:
                    if "divisionName" not in division or not isinstance(division["divisionName"], str):
                        errors.append(f"Division at index {idx} must have a 'divisionName' field of type string")

        # Validate workingDays
        working_days = input_data.get("workingDays")
        if not working_days:
            errors.append("Working days are mandatory and must be a non-empty list")
        elif not isinstance(working_days, list):
            errors.append(f"Working days must be a list")
        else:
            for division_idx, division in enumerate(working_days):
                if not isinstance(division, dict):
                    errors.append(f"Working day at index {division_idx} must be a dictionary")
                    continue

                # Validate divisionName
                division_name = division.get("divisionName")
                if not division_name or not isinstance(division_name, str):
                    errors.append(f"Division at index {division_idx} must have a 'divisionName' field of type string")

                # Validate schedule
                schedule = division.get("schedule")
                if not schedule or not isinstance(schedule, list):
                    errors.append(f"Division '{division_name}' must have a 'schedule' field as a non-empty list")
                else:
                    for schedule_idx, entry in enumerate(schedule):
                        if not isinstance(entry, dict):
                            errors.append(
                                f"Schedule entry at index {schedule_idx} in division '{division_name}' must be a dictionary"
                            )
                            continue

                        # Validate dayName
                        day_name = entry.get("dayName")
                        if not day_name or not isinstance(day_name, str):
                            errors.append(
                                f"Schedule entry {schedule_idx} in division '{division_name}' must have 'dayName' as a string"
                            )

                        # Validate startTime
                        start_time = entry.get("startTime")
                        if not start_time or not isinstance(start_time, str) or is_valid_time_format(start_time) ==False:
                            errors.append(
                                f"Schedule entry {schedule_idx} in division '{division_name}' must have 'startTime' as a string"
                            )

                        # Validate endTime
                        end_time = entry.get("endTime")
                        if not end_time or not isinstance(end_time, str) or is_valid_time_format(end_time) ==False:
                            errors.append(
                                f"Schedule entry {schedule_idx} in division '{division_name}' must have 'endTime' as a string"
                            )

                        # Validate slotSize
                        slot_size = entry.get("slotSize")
                        if not isinstance(slot_size, int) or slot_size <= 0:
                            errors.append(
                                f"Schedule entry {schedule_idx} in division '{division_name}' must have 'slotSize' as a positive integer"
                            )
        # Validate subjects
        subjects = input_data.get("subjects")
        if not subjects:
            errors.append("Subjects are mandatory and must be a non-empty list")
        elif not isinstance(subjects, list):
            errors.append(f"Subjects must be a list")
        else:
            for idx, subject in enumerate(subjects):
                if not isinstance(subject, dict):
                    errors.append(f"Subject at index {idx} must be a dictionary")
                else:
                    if "subjectName" not in subject or not isinstance(subject["subjectName"], str):
                        errors.append(f"Subject at index {idx} must have a 'subjectName' field of type string")

        # Validate faculties
        faculties = input_data.get("faculties")
        if not faculties:
            errors.append("Faculties are mandatory and must be a non-empty list")
        elif not isinstance(faculties, list):
            errors.append(f"Faculties must be a list")
        else:
            for idx, faculty in enumerate(faculties):
                if not isinstance(faculty, dict):
                    errors.append(f"Faculty at index {idx} must be a dictionary")
                else:
                    if "facultyName" not in faculty or not isinstance(faculty["facultyName"], str):
                        errors.append(f"Faculty at index {idx} must have a 'facultyName' field of type string")

        # Validate allotables
        allotable_errors = validate_allotables(input_data=input_data)
        errors.extend(allotable_errors)

        if errors:
            raise Exception("Stage 1 Errors - " + ",\n ".join(errors))
        else:
            print("Stage 1 validation Passed")
            return input_data
    except Exception as e:
        print("Some other errors occured")
        raise Exception(e)