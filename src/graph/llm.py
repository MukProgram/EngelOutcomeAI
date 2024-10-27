import pandas as pd
from rag import engel_score_pipeline
import os
import google.generativeai as genai
import time

def get_training_data():
    df = pd.read_csv('data/engel_scores_output.csv')
    df.dropna(subset=['engel_score', 'reasoning'], inplace=True)
    
    training_data = []
    
    for _, row in df.iterrows():
        data = {}
        data["text_input"] = row['clinical_note']
        
        data["output"] = row['engel_score'] + "\n" + row['reasoning']
        training_data.append(data)
    return training_data

def train_model():
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

    base_model = "models/gemini-1.5-flash-001-tuning"

    operation = genai.create_tuned_model(
        # You can use a tuned model here too. Set `source_model="tunedModels/..."`
        display_name="increment",
        source_model=base_model,
        epoch_count=2,
        batch_size=50,
        learning_rate=0.001,
        training_data=get_training_data(),
    )

    for status in operation.wait_bar():
        time.sleep(1)

    result = operation.result()


    model = genai.GenerativeModel(model_name=result.name)
    return model

def calculate_engel_fine_tune(clinical_note):
    result = train_model().generate_content(engel_score_pipeline(clinical_note))
    return result.text

def calculate_engel_pretrained(clinical_note):
    model = genai.GenerativeModel("gemini-1.5-flash")
    result = model.generate_content(engel_score_pipeline(clinical_note))
    return result.text
        
        
        
    
    

