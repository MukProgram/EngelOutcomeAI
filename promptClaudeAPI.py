"""
This script processes epilepsy clinical notes and prompts Claude to generate an Engel score based on each note.
Claude is further instructed to provide a detailed explanation for the generated Engel score, disregarding the typical post-surgical context of Engel scoring.
The script reads clinical notes from an input directory, sends each note to Claude for scoring, and saves the outputs, including explanations, to an output directory.
"""

import os
import anthropic
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Retrieve the Anthropic API key from an environment variable
API_KEY = os.environ.get('ANTHROPIC_API_KEY')
if not API_KEY:
    raise ValueError("Please set the ANTHROPIC_API_KEY environment variable.")

# Initialize the Anthropic client
client = anthropic.Client(api_key=API_KEY)

# Directories for input notes and output files
input_dir = 'clinical_notes/'
output_dir = 'outputs/'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# List all clinical note files in the input directory
note_files = os.listdir(input_dir)

for note_file in note_files:
    try:
        # Construct full file paths
        input_path = os.path.join(input_dir, note_file)
        output_path = os.path.join(output_dir, f'output_{note_file}')

        # Read the clinical note content
        with open(input_path, 'r', encoding='utf-8') as f:
            clinical_note = f.read()

        # Create the prompt for Claude
        prompt = f"""{anthropic.HUMAN_PROMPT} Please read the following clinical note and generate a plausible Engel score with a detailed explanation for your choice. Ignore the fact that the patient is not post-surgery; instead, provide the probable Engel Score based on the clinical note.

Clinical Note:
{clinical_note}

{anthropic.AI_PROMPT}"""

        # Call the Claude API
        response = client.completion(
            prompt=prompt,
            model="claude-1",  # Update to the specific model you have access to
            max_tokens_to_sample=2000,  # Allows for longer responses
            temperature=0.7,  # Moderate temperature for balanced output
            stop_sequences=[anthropic.HUMAN_PROMPT],
        )

        # Extract the completion text
        output_text = response['completion'].strip()

        # Save the output to a file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_text)

        logging.info(f"Processed '{note_file}' and saved the output to '{output_path}'.")

        # Optional: Pause between requests to respect rate limits
        time.sleep(1)  # Adjust the sleep time as needed

    except Exception as e:
        logging.error(f"Failed to process '{note_file}': {e}")
