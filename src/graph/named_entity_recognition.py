import json
import logging
import anthropic
from tenacity import retry, wait_random_exponential, stop_after_attempt
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Hardcode your API key here
API_KEY = os.getenv("ANTHROPIC_API_KEY")
anthropic_client = anthropic.Anthropic(api_key=API_KEY)

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

# Prepare messages
def system_message(entity_labels, relation_labels):
    return f"""
You are an expert in Natural Language Processing. Your task is to identify Named Entities (NER) and relations in a given text.
The possible Named Entities (NER) types are: ({", ".join(entity_labels)}).
The possible relations are: ({", ".join(relation_labels)}).
"""

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
        "Patient": ["She"]
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

# Chat Completion with Claude
@retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(5))
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
    logging.info(f"Assistant's response: {response_text}")

    # Attempt to parse the response as JSON
    try:
        function_args = json.loads(response_text)
    except json.JSONDecodeError:
        # If parsing fails, try to extract the JSON from the response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                function_args = json.loads(json_str)
            except json.JSONDecodeError as e2:
                logging.error(f"Failed to parse extracted JSON: {e2}")
                function_args = None
        else:
            logging.error("No JSON object found in assistant's response.")
            function_args = None

    if function_args is not None:
        function_response = function_args
    else:
        function_response = None

    return {"model_response": response, "function_response": function_response}

