from src_v3.domain import *
from src_v3.utils.generic_utils import get_new_id, convert_str_to_time
from typing import List, Dict, Literal, Union
from enum import Enum
from src_v3.rules import *
from src_v3.utils.business_utils import DayEnum


def modify_constraints(constraints: List[dict], working_days_list: List[WorkingDay], divisions_list: List[Division]):
    division_id = None
    for constraint in constraints:
        # Handle division name to division ID mapping
        if "divisionName" in constraint:
            division_name = constraint["divisionName"]
            division_id = next(
                (division.id for division in divisions_list if division.name == division_name),
                None
            )
            if division_id is not None:
                constraint["divisionId"] = division_id
            else:
                raise Exception(f"Invalid division name: {division_name}")

    for constraint in constraints:

        # Handle day name to working day ID mapping
        if "dayName" in constraint:
            day_name = constraint["dayName"]
            if day_name != "auto":
                day_id = DayEnum.get_day_id(day_name=day_name.lower())
                
           
                working_day_id = next(
                    (working_day.id for working_day in working_days_list if working_day.day_id == day_id and working_day.division_id == division_id),
                    None
                )
            
                if working_day_id is not None:
                    constraint["workingDayId"] = working_day_id
                else:
                    raise Exception(f"Invalid day name: {day_name}")
            else:
                constraint["workingDayId"] = "auto"

    return constraints


def rule_generator(constraint):
    rule = None
    if "startTime" in constraint and constraint["startTime"] is not None:
        if constraint["startTime"] == 'auto':
            rule = StartTimeRule()
        else:
            rule = StartTimeRule(start_time=convert_str_to_time(constraint["startTime"]))

    elif "endTime" in constraint and constraint["endTime"] is not None:
        if constraint["endTime"] == 'auto':
            rule = EndTimeRule()
        else:
            rule = EndTimeRule(end_time=convert_str_to_time(constraint["endTime"]))

    elif "minimumDailyFrequency" in constraint and constraint["minimumDailyFrequency"] is not None:
        if constraint["minimumDailyFrequency"] == 'auto':
            rule = MinimumDailyFrequencyRule()
        else:
            rule = MinimumDailyFrequencyRule(min_daily_frequency=int(constraint["minimumDailyFrequency"]))

    elif "maximumDailyFrequency" in constraint and constraint["maximumDailyFrequency"] is not None:
        if constraint["maximumDailyFrequency"] == 'auto':
            rule = MaximumDailyFrequencyRule()
        else:
            rule = MaximumDailyFrequencyRule(max_daily_frequency=int(constraint["maximumDailyFrequency"]))

    elif "minimumWeeklyFrequency" in constraint and constraint["minimumWeeklyFrequency"] is not None:
        if constraint["minimumWeeklyFrequency"] == 'auto':
            rule = MinimumWeeklyFrequencyRule()
        else:
            rule = MinimumWeeklyFrequencyRule(min_weekly_frequency=int(constraint["minimumWeeklyFrequency"]))

    elif "maximumWeeklyFrequency" in constraint and constraint["maximumWeeklyFrequency"] is not None:
        if constraint["maximumWeeklyFrequency"] == 'auto':
            rule = MaximumWeeklyFrequencyRule()
        else:
            rule = MaximumWeeklyFrequencyRule(max_weekly_frequency=int(constraint["maximumWeeklyFrequency"]))

    elif "continuousSlot" in constraint and constraint["continuousSlot"] is not None:
        if constraint["continuousSlot"] == 'auto':
            rule = ContinuousSlotRule()
        else:
            rule = ContinuousSlotRule(continuous_slot=int(constraint["continuousSlot"]))

    elif "divisionId" in constraint and constraint["divisionId"] is not None:
        rule = DivisionRule(division_id=constraint["divisionId"])
    elif "workingDayId" in constraint and constraint["workingDayId"] is not None :
        if constraint["workingDayId"] == 'auto':
            rule = WorkingDayRule()
        else:
            rule = WorkingDayRule(working_day_id=constraint["workingDayId"])


    if rule is None:
        raise Exception(f"Rule can't be created for constraint - {constraint}")
    constraint_information = constraint['constraintInformation']
    if constraint_information['type'] == 'soft':
        rule.priority =int(constraint_information['priorityLevel'])
        rule.type = RuleTypesEnum.soft
    return rule
    


def transform(input_data):
    university_id = get_new_id()
    university = University(
        id=university_id,
        logo=input_data.get("logo"),
        name=input_data.get("university_name", university_id)
    )

    divisions_list: List[Division] = []
    working_days_list: List[WorkingDay] = []
    subjects_list: List[Subject] = []
    faculties_list: List[Faculty] = []

    # Process divisions
    for division in input_data["divisions"]:
        new_division = Division(
            id=get_new_id(),
            name=division["divisionName"],
            university_id=university_id,
        )
        divisions_list.append(new_division)

    # Process working days
    for division_days in input_data["workingDays"]:
        for working_day in division_days['schedule']:

            
            day_name = working_day["dayName"].lower()
            working_day_division = next(
                (division for division in divisions_list if division.name == division_days["divisionName"]),
                None
            )
            if not working_day_division:
                raise ValueError(f"Division {division_days['divisionName']} not found for working day {day_name}")

            new_working_day = WorkingDay(
                day=Day(id=DayEnum.get_day_id(day_name), name=day_name),
                day_id=DayEnum.get_day_id(day_name=day_name),
                division=working_day_division,
                id=get_new_id(),
                division_id=working_day_division.id,
                slot_duration=working_day["slotSize"],
                start_time=convert_str_to_time(working_day["startTime"]),
                end_time=convert_str_to_time(working_day["endTime"]),
            )
            working_days_list.append(new_working_day)

    # Process subjects
    for subject in input_data["subjects"]:
        new_subject = Subject(
            id=get_new_id(),
            name=subject['subjectName'],
            university_id=university_id
        )
        subjects_list.append(new_subject)

    # Process faculties
    for faculty in input_data["faculties"]:
        new_faculty = Faculty(
            id=get_new_id(),
            name=faculty['facultyName'],
            university_id=university_id
        )
        faculties_list.append(new_faculty)

    # Process allotables and rules
    slot_allotables = []

    for allotable in input_data["allotables"]:
        constraints = allotable["constraints"]
        rules: List[Rule] = []

        constraints = modify_constraints(constraints=constraints,divisions_list=divisions_list, working_days_list=working_days_list)

        for constraint in constraints:
            rule = rule_generator(constraint=constraint)
            rules.append(rule)

        # Resolve entity
        entity: AllotableEntity = None
        if allotable["entity"]["type"] == "subjectFacultyDivision":
            entity_division = next(
                (division for division in divisions_list if division.name == allotable["entity"]["divisionName"]),
                None
            )
            entity_faculty = next(
                (faculty for faculty in faculties_list if faculty.name == allotable["entity"]["facultyName"]),
                None
            )
            entity_subject = next(
                (subject for subject in subjects_list if subject.name == allotable["entity"]["subjectName"]),
                None
            )

            if not entity_division or not entity_faculty or not entity_subject:
                raise ValueError(f"Invalid entity data for {allotable['entity']}")

            entity = FacultySubjectDivision(
                id=get_new_id(),
                name=f'{allotable["entity"]["subjectName"]}-{allotable["entity"]["divisionName"]}-{allotable["entity"]["facultyName"]}',
                division=entity_division,
                faculty=entity_faculty,
                subject=entity_subject,
                subject_id=entity_subject.id,
                division_id=entity_division.id,
                faculty_id=entity_faculty.id
            )
        elif allotable["entity"]["type"] == "break":
            entity = Break(id=get_new_id(), name=allotable["entity"]["name"])
        elif allotable["entity"]["type"] == "empty":
            entity = Proxy(id=get_new_id(), name="empty")

        # Assign rules and create SlotAllotable
        start_time_rule = next((rule for rule in rules if isinstance(rule, StartTimeRule)), None)
        end_time_rule = next((rule for rule in rules if isinstance(rule, EndTimeRule)), None)
        continuous_slot_rule = next((rule for rule in rules if isinstance(rule, ContinuousSlotRule)), None)
        min_daily_frequency_rule = next((rule for rule in rules if isinstance(rule, MinimumDailyFrequencyRule)), None)
        max_daily_frequency_rule = next((rule for rule in rules if isinstance(rule, MaximumDailyFrequencyRule)), None)
        minimum_weekly_frequency_rule = next((rule for rule in rules if isinstance(rule, MinimumWeeklyFrequencyRule)), None)
        maximum_weekly_frequency_rule = next((rule for rule in rules if isinstance(rule, MaximumWeeklyFrequencyRule)), None)
        division_rule = next((rule for rule in rules if isinstance(rule, DivisionRule)), None)
        working_day_rule = next((rule for rule in rules if isinstance(rule, WorkingDayRule)), None)

        division = next(
            (division for division in divisions_list if division.id == division_rule.division_id),
            None
        )        

        working_day = next(
            (working_day for working_day in working_days_list if working_day.id == working_day_rule.working_day_id),
            None
        ) 
        working_day_id = working_day.id if working_day is not None else None

        slot_allotable = SlotAllotable(
            allotable_entity=entity,
            allotable_entity_id=entity.id,
            id=get_new_id(),
            continuous_slot_rule=continuous_slot_rule,
            division_rule =division_rule,
            maximum_daily_frequency_rule=max_daily_frequency_rule,
            minimum_daily_frequency_rule=min_daily_frequency_rule,
            minimum_weekly_frequency_rule=minimum_weekly_frequency_rule,
            maximum_weekly_frequency_rule=maximum_weekly_frequency_rule,
            end_time_rule=end_time_rule,
            start_time_rule=start_time_rule,
            working_day_rule=working_day_rule,
            division_id=division_rule.division_id,
            next_slot_allotable=None,
            next_slot_allotable_id=None,
            division=division,
            working_day=working_day,
            working_day_id=working_day_id

        )
        slot_allotables.append(slot_allotable)

    # Return or save transformed data
    return {
        "university": university,
        "divisions": divisions_list,
        "working_days": working_days_list,
        "subjects": subjects_list,
        "faculties": faculties_list,
        "slot_allotables": slot_allotables,
    }
