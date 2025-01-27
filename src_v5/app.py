from src_v5.domain.university import *
from src_v5.utils.generic_utils import convert_str_to_time
# from src_v5.ga_exec_simple import generate_timetable
from src_v5.ga_exec_simple_v2 import generate_timetable




# ------------ DAYS--------------------
monday = Day(id=get_new_id(),name='monday')
tuesday = Day(id=get_new_id(),name='tuesday')
wednesday = Day(id=get_new_id(),name='wednesday')
thursday = Day(id=get_new_id(),name='thursday')
friday = Day(id=get_new_id(),name='friday')





orchestra = Orchestra()
# ----------- CREATE UNIVERSITY ------------------
university  = orchestra.create_university(name="SAKEC")


# -------------- WORKING HOURS ---------------------
start_time = convert_str_to_time("09:00am")
end_time = convert_str_to_time("05:00pm")

working_hours = WorkingHours(id=get_new_id(),start_time=start_time, end_time=end_time)


# ------------- WORKING DAYS ----------------------
university_working_day_1 = WorkingDay(id=get_new_id(), day=monday, working_hours=[working_hours])
university_working_day_2 = WorkingDay(id=get_new_id(), day=tuesday, working_hours=[working_hours])
university_working_day_3 = WorkingDay(id=get_new_id(), day=wednesday, working_hours=[working_hours])
university_working_day_4 = WorkingDay(id=get_new_id(), day=thursday, working_hours=[working_hours])
university_working_day_5 = WorkingDay(id=get_new_id(), day=friday, working_hours=[working_hours])



#  -------------- WORKING WEEK ---------------------------------

university_working_week_skeleton = WorkingWeekSkeleton(id=get_new_id(),slot_duration=60,working_days=[
    university_working_day_1,university_working_day_2,university_working_day_3,university_working_day_4, university_working_day_5
])


#  ------------ SET UNIVERIST
university.working_week_skeleton = university_working_week_skeleton

#  ----------------- DIVISIONS -----------------------
div_1 = orchestra.create_division_for_university(name="DIV1",university=university)
div_2 = orchestra.create_division_for_university(name="DIV2",university=university)




div_1_working_week = orchestra.clone_working_week_skeleton(university_working_week_skeleton)

div_2_working_week = orchestra.clone_working_week_skeleton(university_working_week_skeleton)


# --------------- ASSIGN WORKING WEEK TO DIVISION -----------------
div_1.set_working_week_skeleton(div_1_working_week)
div_2.set_working_week_skeleton(div_2_working_week)




# -------------- CREATE SLOTS FOR DIVISIONS ----------------------------
div_1_slots = orchestra.create_slots_for_division(div_1)
div_2_slots = orchestra.create_slots_for_division(div_2)

slots = div_1_slots + div_2_slots




# ------------------- SUBJECTS -----------------------

subject_1 =Subject(id=get_new_id(),name="subject_1")
subject_2 =Subject(id=get_new_id(),name="subject_2")
subject_3 =Subject(id=get_new_id(),name="subject_3")
subject_4 =Subject(id=get_new_id(),name="subject_4")
subject_5 =Subject(id=get_new_id(),name="subject_5")
subject_6 =Subject(id=get_new_id(),name="subject_6")
subject_7 =Subject(id=get_new_id(),name="subject_7")
subject_8 =Subject(id=get_new_id(),name="subject_8")
subject_9 =Subject(id=get_new_id(),name="subject_9")
subject_10 =Subject(id=get_new_id(),name="subject_10")


# ------------------- FACULTIES ---------------------
faculty_1 = Faculty(id=get_new_id(), availability_skeleton=orchestra.clone_working_week_skeleton(university_working_week_skeleton), name="Faculty 1")
faculty_2 = Faculty(id=get_new_id(), availability_skeleton=orchestra.clone_working_week_skeleton(university_working_week_skeleton), name="Faculty 2")
faculty_3 = Faculty(id=get_new_id(), availability_skeleton=orchestra.clone_working_week_skeleton(university_working_week_skeleton), name="Faculty 3")
faculty_4 = Faculty(id=get_new_id(), availability_skeleton=orchestra.clone_working_week_skeleton(university_working_week_skeleton), name="Faculty 4")
faculty_5 = Faculty(id=get_new_id(), availability_skeleton=orchestra.clone_working_week_skeleton(university_working_week_skeleton), name="Faculty 5")
faculty_6 = Faculty(id=get_new_id(), availability_skeleton=orchestra.clone_working_week_skeleton(university_working_week_skeleton), name="Faculty 6")


# -------------------  ENTITIES ----------------------

entity_1 = TeachingEntity(id=get_new_id(), continuous_slot=1,maximum_weekly_frequency=5, division=div_1, subject=subject_1, faculty=faculty_1)
entity_2 = TeachingEntity(id=get_new_id(), continuous_slot=1,maximum_weekly_frequency=5, division=div_2, subject=subject_1, faculty=faculty_1)
entity_3 = TeachingEntity(id=get_new_id(), continuous_slot=2,maximum_weekly_frequency=6, division=div_1, subject=subject_2, faculty=faculty_2)
entity_4 = TeachingEntity(id=get_new_id(), continuous_slot=2,maximum_weekly_frequency=6, division=div_2, subject=subject_2, faculty=faculty_3)

entity_5 = NonTeachingEntity(id=get_new_id(), continuous_slot=1, maximum_weekly_frequency=5,division=div_1, name='LUNCH')
entity_6 = NonTeachingEntity(id=get_new_id(), continuous_slot=1, maximum_weekly_frequency=5,division=div_2, name='LUNCH')


entities = [
    entity_1,entity_2,entity_3,entity_4,entity_5,entity_6
]

allotables = orchestra.create_slot_allotables_for_entities(entities=entities)

final_input = {
    "university":university,
    "divisions":[
        div_1, div_2
    ],
    "slots":slots,
    "allotables":allotables
}

save_output_file('ongoing_1.json',final_input)

try:
    final_chromosome = generate_timetable(final_input)
except KeyboardInterrupt:
    print("Stopped manually")

import os

university_id = final_chromosome.genes[0].division.university.id
# save_output_file(f"{university_id}.json",{"university_slots":final_chromosome})
save_output_file(f"final_1.json",{"university_slots":final_chromosome.genes})


import os
curr_path = os.path.dirname(__file__)
# output_path = os.path.join(curr_path, f"data/outputs/{university_id}.json")
output_path = os.path.join(curr_path, f"data/outputs/final_1.json")

json_data = read_json_data(output_path)
json_data = json.dumps(json_data)

from src_v5.pdf_service.generate import generate_timetable_pdfs

generate_timetable_pdfs(json_data)
