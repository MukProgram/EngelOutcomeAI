import os
import json
import csv
import re
import string
from datetime import datetime
import time
import bs4 as bs
import contractions
import nltk
import pandas as pd
import requests
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from num2words import num2words
import roman

# Ensure necessary NLTK data packages are downloaded
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)  # Corrected from 'punkt_tab' to 'punkt'
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)  # Corrected from 'averaged_perceptron_tagger_eng' to 'averaged_perceptron_tagger'

def preprocess_note(note):
    """
    Preprocess the clinical note by:
    - Lowercasing
    - Expanding contractions
    - Converting numbers and percentages to words
    - Removing punctuation
    - Tokenizing
    - Removing stop words (excluding negations)
    - Lemmatizing
    - Handling negations
    - Expanding medical abbreviations
    """
    def replace_numbers_and_percentages(text):
        """
        Replace all numbers and percentages in a string with their English word equivalents.
        """
        number_pattern = re.compile(r'(\d+(\.\d+)?%?)')

        def convert_number_to_words(match):
            number_str = match.group(0)
            if '%' in number_str:
                number = float(number_str.replace('%', ''))
                number_in_words = num2words(number) + ' percent'
            else:
                number = float(number_str)
                number_in_words = num2words(number)
            return number_in_words

        return number_pattern.sub(convert_number_to_words, text)

    def get_wordnet_pos(treebank_tag):
        """
        Convert TreeBank POS tags to WordNet POS tags for lemmatization.
        """
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN

    def remove_stop_words(toks):
        stop_words = set(stopwords.words('english')) - negation_words
        return [word for word in toks if word not in stop_words]

    def lemmatize_tokens(toks):
        lemmatizer = WordNetLemmatizer()
        pos_tags = nltk.pos_tag(toks)
        lemmatized_toks = [lemmatizer.lemmatize(token, get_wordnet_pos(pos)) for token, pos in pos_tags]
        return lemmatized_toks

    def handle_negation(toks):
        negated_toks = []
        negate = False
        for token in toks:
            if token in negation_words:
                negate = True
                continue
            if negate:
                negated_toks.append('not_' + token)
                negate = False
            else:
                negated_toks.append(token)
        return negated_toks
    
    # --------------------- Medical Abbreviations Dictionary --------------------- #
    # Comprehensive dictionary mapping medical abbreviations to their expanded forms
    MEDICAL_ABBREVIATIONS = {
        # Vital Signs
        "BP": "blood pressure",
        "HR": "heart rate",
        "RR": "respiratory rate",
        "Temp": "temperature",
        "O2": "oxygen",
        "SpO2": "peripheral capillary oxygen saturation",
        "BPM": "beats per minute",

        # Routes of Administration
        "IV": "intravenous",
        "IM": "intramuscular",
        "PO": "by mouth",
        "PRN": "as needed",
        "SL": "sublingual",
        "TOP": "topical",
        "SC": "subcutaneous",
        "GTT": "gtt",

        # Medical Procedures and Tests
        "ECG": "electrocardiogram",
        "EKG": "electrocardiogram",
        "MRI": "magnetic resonance imaging",
        "CT": "computed tomography",
        "US": "ultrasound",
        "CXR": "chest x-ray",
        "CBC": "complete blood count",
        "CMP": "comprehensive metabolic panel",
        "ABG": "arterial blood gas",
        "EEG": "electroencephalogram",
        "PET": "positron emission tomography",
        "DVT": "deep vein thrombosis",
        "PT": "physical therapy",
        "OT": "occupational therapy",
        "STAT": "immediately",
        "ASAP": "as soon as possible",
        "AIDET": "acknowledge, introduce, duration, explanation, thank you",

        # Common Conditions and Diagnoses
        "COPD": "chronic obstructive pulmonary disease",
        "CHF": "congestive heart failure",
        "CAD": "coronary artery disease",
        "DM": "diabetes mellitus",
        "HTN": "hypertension",
        "PE": "pulmonary embolism",
        "TIA": "transient ischemic attack",
        "MI": "myocardial infarction",
        "CVA": "cerebrovascular accident",
        "AKI": "acute kidney injury",
        "CKD": "chronic kidney disease",
        "UTI": "urinary tract infection",
        "GERD": "gastroesophageal reflux disease",
        "OSA": "obstructive sleep apnea",
        "H&P": "history and physical",
        "CC": "chief complaint",
        "HPI": "history of present illness",
        "ROS": "review of systems",
        "PMHx": "past medical history",
        "FHx": "family history",
        "SHx": "social history",
        "PE": "physical examination",
        "VS": "vital signs",
        "LOC": "level of consciousness",
        "A&O": "alert and oriented",
        "A&O x 3": "alert and oriented to person, place, and time",
        "Q2H": "every two hours",
        "Q4H": "every four hours",
        "Q6H": "every six hours",
        "Q8H": "every eight hours",
        "QOD": "every other day",
        "CID": "three times a day",

        # Medications and Treatments
        "Rx": "prescription",
        "OTC": "over-the-counter",
        "NSAID": "nonsteroidal anti-inflammatory drug",
        "ASA": "acetylsalicylic acid",
        "PTSD": "post-traumatic stress disorder",
        "AED": "anti-epileptic drug",
        "ACEi": "angiotensin-converting enzyme inhibitor",
        "ARBs": "angiotensin II receptor blockers",
        "BB": "beta-blocker",
        "CNS": "central nervous system",
        "PNS": "peripheral nervous system",
        "TID": "three times daily",
        "BID": "twice daily",
        "QID": "four times daily",
        "HS": "at bedtime",
        "QD": "once daily",
        "PRN": "as needed",
        "SOB": "shortness of breath",
        "N/V": "nausea and vomiting",
        "LOC": "loss of consciousness",
        "A&O": "alert and oriented",
        "A&O x 3": "alert and oriented to person, place, and time",

        # Laboratory Values
        "Na+": "sodium",
        "K+": "potassium",
        "Cl-": "chloride",
        "HCO3-": "bicarbonate",
        "Gluc": "glucose",
        "Hb": "hemoglobin",
        "Hct": "hematocrit",
        "WBC": "white blood cell count",
        "RBC": "red blood cell count",
        "Plt": "platelets",
        "Cr": "creatinine",
        "BUN": "blood urea nitrogen",
        "AST": "aspartate aminotransferase",
        "ALT": "alanine aminotransferase",
        "ALP": "alkaline phosphatase",
        "INR": "international normalized ratio",
        "PTT": "partial thromboplastin time",
        "LDH": "lactate dehydrogenase",
        "TSH": "thyroid-stimulating hormone",

        # Anatomical Terms
        "CNS": "central nervous system",
        "PNS": "peripheral nervous system",
        "GI": "gastrointestinal",
        "GU": "genitourinary",
        "ENT": "ear, nose, throat",
        "MSK": "musculoskeletal",
        "HEENT": "head, eyes, ears, nose, throat",

        # Miscellaneous
        "NPO": "nothing by mouth",
        "ADL": "activities of daily living",
        "H&P": "history and physical",
        "CC": "chief complaint",
        "HPI": "history of present illness",
        "ROS": "review of systems",
        "PMHx": "past medical history",
        "FHx": "family history",
        "SHx": "social history",
        "PE": "physical examination",
        "Dx": "diagnosis",
        "Tx": "treatment",
        "Sx": "symptoms",
        "Fx": "fracture",
        "LMP": "last menstrual period",
        "D/C": "discontinue or discharge",
        "BID": "twice a day",
        "CID": "three times a day",
        "Q2H": "every two hours",
        "Q4H": "every four hours",
        "Q6H": "every six hours",
        "Q8H": "every eight hours",
        "PRN": "as needed",
        "SOB": "shortness of breath",
        "N/V": "nausea and vomiting",
        "LOC": "level of consciousness",
        "A&O": "alert and oriented",
        "A&O x 3": "alert and oriented to person, place, and time",
        "VS": "vital signs",
        "PR": "pulse rate"
    }

    def expand_medical_abbreviations(text):
        """
        Expand medical abbreviations in the text using MEDICAL_ABBREVIATIONS dictionary.
        """
        pattern = re.compile(r'\b(' + '|'.join(map(re.escape, MEDICAL_ABBREVIATIONS.keys())) + r')\b', flags=re.IGNORECASE)

        def replace(match):
            abbr = match.group(0)
            expanded = MEDICAL_ABBREVIATIONS.get(abbr.upper(), abbr)
            return expanded.lower()

        return pattern.sub(replace, text)

    # Define negation words
    negation_words = {'not', 'no', 'never', 'neither', 'nor', 'nobody', "n't"}

    # Step-by-step preprocessing
    note = note.lower()  # Lowercasing
    note = contractions.fix(note)  # Expanding contractions
    note = replace_numbers_and_percentages(note)  # Converting numbers and percentages to words
    note = re.sub(r'[^\w\s]', '', note)  # Removing punctuation
    toks = nltk.word_tokenize(note)  # Tokenizing
    toks = remove_stop_words(toks)  # Removing stop words
    toks = lemmatize_tokens(toks)  # Lemmatizing
    toks = handle_negation(toks)  # Handling negations
    preprocessed_note = expand_medical_abbreviations(' '.join(toks))  # Expanding medical abbreviations

    return preprocessed_note

# Define paths to directories and output file
clinical_notes_dir = 'data/clinical_notes'
engel_scores_dir = 'data/synthetic_engel_scores'
output_csv = 'data/engel_scores_output.csv'

json_pattern = r'```json\n({.*?})\n```'

df = pd.DataFrame(columns=['clinical_note', 'engel_score', 'reasoning'])

# Iterate over clinical notes
for note_file in os.listdir(clinical_notes_dir):
    
    with open(os.path.join(clinical_notes_dir, note_file), 'r') as f:
        note_text = f.read()
    
    # Preprocess clinical note
    preprocessed_note = preprocess_note(note_text)
    
    # get corresponding synthetic engel score file'
    engel_score_file = os.path.join(engel_scores_dir, f"output_{note_file}")
    with open(engel_score_file, 'r') as f:
        engel_score_data = f.read()

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

    





