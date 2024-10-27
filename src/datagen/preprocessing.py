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

    def extract_json(text):
        json_pattern = r'```json\n({.*?})\n```'
        json_matches = re.findall(json_pattern, text, re.DOTALL) 
        if json_matches:
            return json_matches[0]
        return None

    json_data = extract_json(engel_score_data)
    if json_data:
        try:
            json_data = json_data.replace('\\"', '"')
            json_data = json.loads(json_data)
            
            engel_score = json_data['score']
            reasoning = json_data['reasoning']
        except Exception as e:
            print(f"Error parsing JSON in file: {engel_score_file}")
            print(e)
            engel_score = None
            reasoning = None
    else:
        engel_score = None
        reasoning = None
    
    # check if the engel score is a list or string. if it is list convert to str
    if isinstance(engel_score, list):
        engel_score = ' '.join(engel_score)
    
    new_row = pd.DataFrame([{'clinical_note': preprocessed_note, 'engel_score': engel_score, 'reasoning': reasoning}])
    df = pd.concat([df, new_row], ignore_index=True)

else:
    print(f"No JSON pattern found in file: {engel_score_file}")
    # check if the engel score is a list or string. if it is list convert to str
    if isinstance(engel_score, list):
        engel_score = ' '.join(engel_score)
    

# Save dataframe to CSV
df.to_csv(output_csv, index=False)

    





