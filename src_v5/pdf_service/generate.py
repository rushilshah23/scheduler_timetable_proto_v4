import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import json
from typing import List

# Helper function to derive entity name
def get_entity_name(slot):
    if slot["slot_alloted_to"]:
        entity = slot["slot_alloted_to"]["allotable_entity"]
        if entity["type"] == "TeachingEntity":
            division_name = entity["division"]["name"]
            subject_name = entity["subject"]["name"]
            faculty_name = entity["faculty"]["name"]
            return f"{subject_name}-{faculty_name}-{division_name}-{slot['slot_alloted_to']['continuous_left']}"
        elif entity["type"] == "NonTeachingEntity":
            division_name = entity["division"]["name"]

            return f'{entity["name"]}-{division_name}'
    return "EMPTY"

# Function to generate timetable PDF for a division
# Function to generate timetable PDF for a division
def generate_pdf_for_division(division_name, slots, output_dir):
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = f"{output_dir}/{division_name}_timetable.pdf"
    pdf = SimpleDocTemplate(filename, pagesize=letter)

    # Extract unique weekdays and slot timings
    weekdays = sorted(list({slot["working_day"]["day"]["name"] for slot in slots}))
    slot_timings = sorted(list({
        (slot["slot_time"]["start_time"], slot["slot_time"]["end_time"])
        for slot in slots
    }))

    # Initialize table data
    data = [["Slot Timing"] + weekdays]

    # Populate data with empty rows for each slot timing
    timing_to_row = {}
    for idx, timing in enumerate(slot_timings):
        start_time, end_time = timing
        row = [f"{start_time} - {end_time}"] + ["EMPTY" for _ in weekdays]
        data.append(row)
        timing_to_row[timing] = idx + 1  # Map timing to row index

    # Fill in the table with slot data
    day_to_col = {day: idx + 1 for idx, day in enumerate(weekdays)}  # Map day to column index
    for slot in slots:
        day = slot["working_day"]["day"]["name"]
        start_time = slot["slot_time"]["start_time"]
        end_time = slot["slot_time"]["end_time"]
        timing = (start_time, end_time)
        row_idx = timing_to_row[timing]
        col_idx = day_to_col[day]
        data[row_idx][col_idx] = get_entity_name(slot)

    # Create table with style
    table = Table(data)
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),  # Header font size
        ("FONTSIZE", (0, 1), (-1, -1), 8),  # Data font size
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),  # Reduce padding for data rows
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),  # Thinner grid
    ])

    table.setStyle(style)

    # Build PDF
    pdf.build([table])
    print(f"Timetable generated: {filename}")

# Main function to process slots and generate PDFs
def generate_timetable_pdfs(slots_json, output_dir="output"):
    # Parse JSON into a dictionary
    university_slots = json.loads(slots_json)
    slots = university_slots['university_slots']

    # Group slots by division
    divisions = {}
    for slot in slots:
        division_name = slot["division"]["name"]  # Use division name from JSON
        if division_name not in divisions:
            divisions[division_name] = []
        divisions[division_name].append(slot)

    # Generate PDF for each division
    for division_name, division_slots in divisions.items():
        generate_pdf_for_division(division_name, division_slots, output_dir)
