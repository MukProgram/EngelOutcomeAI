import json
import logging
import anthropic
from tenacity import retry, wait_random_exponential, stop_after_attempt
import os
import re
import time


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# Define the NER labels to be identified, based on your updated schema
entity_labels = [
    "PastDiagnoses", "SeizureOnset", "SeizureChange", "Symptoms", "ProvocationSeizureAura",
    "SeizureSeverity", "SeizurePropagation", "SeizurePalliation", "MedicationHistory",
    "Age", "EpilepsySurgery", "FrequencyOfSeizures", "Patient"
]

# Define relation labels to identify, based on your updated schema
relation_labels = [
    "HAS", "EXPERIENCES", "PROVOKED_BY", "IMPACTS", "ASSOCIATED_WITH",
    "IMPROVES", "WORSENS", "UNDERGOES", "LEADS_TO"
]

# Prepare system query 
def system_message(entity_labels, relation_labels):
    return f"""
You are an expert in Natural Language Processing. Your task is to identify Named Entities (NER) and relations in a given text.
The possible Named Entities (NER) types are: ({", ".join(entity_labels)}).
The possible relations are: ({", ".join(relation_labels)}).
A relation is a directed edge between two entities. For example, "HAS" is a relation between a PATIENT and a epilepsy. and LEADS_TO is a relation between  a seizure and brain damage. 
Make sure to generate many relations as possible from the text.
"""

# Prepare structure
def assistant_message():
    return f"""
EXAMPLE:
    Text: 'The 50-year-old patient has a history of probable generalized epilepsy and experiences generalized seizures every two months. She injured herself and bit her tongue during a seizure episode. Her epilepsy began in childhood but reappeared five years ago. Currently, she is on sodium valproate and levetiracetam.'
{{
    "Entities": {{
        "PastDiagnoses": ["probable generalized epilepsy"],
        "Age": ["50-year-old"],
        "FrequencyOfSeizures": ["every two months"],
        "SeizureOnset": ["began in childhood", "reappeared five years ago"],
        "SeizureRelatedInjuries": ["injured herself", "bit her tongue"],
        "MedicationHistory": ["sodium valproate", "levetiracetam"],
        "Patient": ["Patient"]
    }},
    "Relations": [
        {{"type": "HAS", "source": "She", "target": "probable generalized epilepsy"}},
        {{"type": "EXPERIENCES", "source": "She", "target": "bit her tongue"}},
        {{"type": "LEADS_TO", "source": "began in childhood", "target": "probably generalized epilepsy"}}
    ]
}}
--"""

def user_message(text):
    return f"""
TASK:
    Text: {text}
"""

# NER Core function
def get_entities_relations(entity_labels, relation_labels, text):
    # Build the prompt
    prompt = (
        f"{anthropic.HUMAN_PROMPT}{system_message(entity_labels, relation_labels)}\n"
        f"{assistant_message()}\n"
        f"{user_message(text)}\n"
        "Please output only the JSON object containing the recognized entities and relations.\n"
        f"{anthropic.AI_PROMPT}"
    )

    response = anthropic_client.completions.create(
        model="claude-2",
        prompt=prompt,
        stop_sequences=[anthropic.HUMAN_PROMPT],
        max_tokens_to_sample=1000,
        temperature=0,
        top_p=1,
    )

    response_text = response.completion.strip()
    
    # Parse the json response within response_text into a dict
    matches = re.search(r'\{.*\}', response_text, re.DOTALL)
    
    # convert match object to string then dict
    response_text = json.loads(matches.group())
    if 'Patient' in response_text['Entities'] != ['Patient']:
        response_text['Entities']['Patient'] = ['Patient']

    return response_text

def execute_ner(text):
    response = get_entities_relations(entity_labels, relation_labels, text)
    return response

clinical_note = """

The 50 year old patient has a history of probable generalized epilepsy and experiences generalized seizures every two months. She injured herself and bit her tongue during a seizure episode. Her epilepsy began in childhood but reappeared five years ago. Currently, she is on sodium valproate and levetiracetam.

"""

print(execute_ner(clinical_note))