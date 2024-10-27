import os
import logging
import time
import random
from anthropic import Anthropic

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Directories for input notes and output files
input_dir = 'data/clinical_notes'
output_dir = 'data/'
os.makedirs(output_dir, exist_ok=True)
note_files = os.listdir(input_dir)

for note_file in note_files:
    try:
        # Construct full file paths
        input_path = os.path.join(input_dir, note_file)
        output_path = os.path.join(output_dir, f'output_{note_file}')

        # Read the clinical note content
        with open(input_path, 'r', encoding='utf-8') as f:
            clinical_note = f.read()

        # Create the message content
        message_content = f"""
Please review the clinical note provided below and assess the patient using the Engel Outcome Scale criteria listed afterward. Assign an Engel score (number and letter) to the patient, even if certain aspects of the criteria are unclear or missing. For this task, ignore whether or not the patient is post-surgery. If and only if there are multiple possible scores with valid reasoning, provide all possible scores and their reasoning as a list.

**Engel Outcome Scale**:
Class I: Free of disabling seizures

IA: Completely seizure-free since surgery
IB: Non disabling simple partial seizures only since surgery
IC: Some disabling seizures after surgery, but free of disabling seizures for at least 2 years
ID: Generalized convulsions with antiepileptic drug withdrawal only

Class II: Rare disabling seizures (“almost seizure-free”)

IIA: Initially free of disabling seizures but has rare seizures now
IIB: Rare disabling seizures since surgery
IIC: More than rare disabling seizures after surgery, but rare seizures for at least 2 years
IID: Nocturnal seizures only

Class III: Worthwhile improvement

IIIA: Worthwhile seizure reduction
IIIB: Prolonged seizure-free intervals amounting to greater than half the follow-up period, but not less than 2 years

Class IV: No worthwhile improvement

IVA: Significant seizure reduction
IVB: No appreciable change
IVC: Seizures worse.

**Clinical Note:**
{clinical_note}

**Output Requirements:**
1. **Engel Score**: Provide the score as a number and letter (e.g., "1A").
2. **Reasoning**: Write a thorough explanation for the chosen score, detailing the clinical reasoning behind your decision.
3. **Variations** If and only if there are multiple possible scores with valid reasoning, provide all possible scores and their reasoning as a list.

Return the results in JSON format, structured as follows:
```json
{{
  "score": "<Engel Score>",
  "reasoning": "<Detailed clinical reasoning>"
}}
"""
        
        # Format the prompt as per Anthropic API requirements
        prompt = f"\n\nHuman: {message_content}\n\nAssistant:"

        response = client.completions.create(
            model="claude-2",
            max_tokens_to_sample=2000,
            temperature=0.7,
            prompt=prompt
        )
        output_text = response.completion.strip()

        # Save the output to a file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_text)

        logging.info(f"Processed '{note_file}' and saved the output to '{output_path}'.")

        time.sleep(random.uniform(2, 5))  # rate limit

    except Exception as e:
        logging.error(f"Failed to process '{note_file}': {e}")
        if '429' in str(e):
            logging.info("Rate limit exceeded. Sleeping for 60 seconds.")
            time.sleep(60)
            continue