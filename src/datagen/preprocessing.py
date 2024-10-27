import os
import json
import csv
import re

# Paths to directories
clinical_notes_dir = 'data/clinical_notes'
engel_scores_dir = 'data/synthetic_engel_scores'

# CSV output file path
output_csv = 'engel_scores_output.csv'

# Regular expression to extract JSON content from the text
json_pattern = r'```json\n({.*?})\n```'

# Open the CSV file for writing
with open(output_csv, mode='w', newline='') as csv_file:
    fieldnames = ['clinical_note', 'engel_score', 'reasoning']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # Loop through each file in the clinical notes directory
    for clinical_note_filename in os.listdir(clinical_notes_dir):
        # Construct clinical note path
        clinical_note_path = os.path.join(clinical_notes_dir, clinical_note_filename)

        # Read the clinical note text
        with open(clinical_note_path, 'r') as clinical_note_file:
            clinical_note_text = clinical_note_file.read()

        # Match corresponding Engel score filename
        engel_score_filename = f"output_{clinical_note_filename}"
        engel_score_path = os.path.join(engel_scores_dir, engel_score_filename)

        # Check if the Engel score file exists
        if os.path.exists(engel_score_path):
            # Read the Engel score file
            with open(engel_score_path, 'r') as engel_score_file:
                engel_score_content = engel_score_file.read()

                # Find all JSON blocks in the file
                json_matches = re.findall(json_pattern, engel_score_content, re.DOTALL)

                # Process each JSON block found
                for json_text in json_matches:
                    try:
                        # Parse the JSON content
                        engel_data = json.loads(json_text)
                        score = engel_data.get("score", "")
                        reasoning = engel_data.get("reasoning", "")

                        # Write to CSV
                        writer.writerow({
                            'clinical_note': clinical_note_text,
                            'engel_score': score,
                            'reasoning': reasoning
                        })

                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {engel_score_filename}: {e}")

print("CSV file created successfully.")
