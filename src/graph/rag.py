import requests
import pandas as pd
from neo4j import GraphDatabase
import logging

# api key gemni: AIzaSyCwPO_wC8UjEgYa8Y_SW_rkqkGv6e58uf0

logging.basicConfig(level=logging.DEBUG)

# Neo4j configuration
neo4j_uri = "neo4j+s://a3ccaeb7.databases.neo4j.io"
neo4j_user = "neo4j"
neo4j_password = "TzR6rQkvmPBm25_LJcd9AIclvx4sgH4z9mKqfbQVqXI"

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

def retrieve_knowledge_graph_context(clinical_entities):
    """
    Queries the knowledge graph to find related data based on clinical entities.
    :param clinical_entities: List of entities to search in the knowledge graph.
    :return: List of retrieved data.
    """
    query = """
    MATCH (n)-[r]->(m)
    WHERE ANY(entity IN $clinical_entities WHERE n.name CONTAINS entity OR m.name CONTAINS entity)
    RETURN n.name AS Entity1, type(r) AS Relationship, m.name AS Entity2
    """
    with driver.session() as session:
        result = session.run(query, clinical_entities=clinical_entities)
        data = [{"Entity1": record["Entity1"], "Relationship": record["Relationship"], "Entity2": record["Entity2"]} for record in result]
        return data

def prepare_input_for_gemini(clinical_ner, knowledge_graph_data):
    """
    Prepares the input for the Gemini API.
    :param clinical_notes: Original clinical notes.
    :param knowledge_graph_data: Retrieved knowledge graph context.
    :return: Formatted prompt for Gemini.
    """
    context_text = " ".join([f"{data['Entity1']} ({data['Relationship']}) {data['Entity2']}" for data in knowledge_graph_data])
    prompt = f"""
    Clinical Notes: {clinical_ner}

    Context from Knowledge Graph: {context_text}

    Based on this information, predict the Engel score and provide reasoning for your prediction.
    Class I: Free of disabling seizures

    IA: Completely seizure-free since surgery
    IB: Non disabling simple partial seizures only since surgery
    IC: Some disabling seizures after surgery, but free of disabline seizures for at least 2 years
    ID: Generalized convulsions with antiepileptic drug withdrawal only

    Class II: Rare disabling seizures (“almost seizure-free”)

    IIA: Initially free of disabling seizures but has rare seizures now
    IIB: Rare disabling seizures since surgery
    IIC: More than rare disabling seiuzres after surgery, but rare seizures for at least 2 years
    IID: Nocturnal seizures only

    Class III: Worthwhile improvement

    IIIA: Worthwhile seiuzre reduction
    IIIB: Prolonged seiuzre-free intervals amounting to greater than half the follow-up period, but not less than 2 years
    Class IV: No worthwhile improvement
    IVA: Significant seizure reduction
    IVB: No appreciable change
    IVC: Seizures worse

    """
    return prompt

# ret input text for predictive model
def call_fine_tuned_model(input_text, api_key):
    """
    Calls the fine-tuned model to get Engel score and explanation.
    :param input_text: The formatted input for the fine-tuned model.
    :return: Response from the fine-tuned model.
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyCwPO_wC8UjEgYa8Y_SW_rkqkGv6e58uf0"  # Replace with your fine-tuned model endpoint
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "prompt": input_text,
        "max_tokens": 500  # Adjust based on your requirements
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

def engel_score_pipeline(clinical_notes, api_key):
    # Step 1: Extract clinical entities from notes
    clinical_entities = clinical_notes.split()

    # Step 2: Retrieve knowledge graph context
    knowledge_graph_data = retrieve_knowledge_graph_context(clinical_entities)
    
    # Step 3: Prepare input for fine-tuned model
    input_text = call_fine_tuned_model(clinical_notes, knowledge_graph_data)
    
    # Step 4: Call fine-tuned model to get Engel score and explanation
    model_response = call_fine_tuned_model(input_text, api_key)
    predicted_engel_score = model_response.get('predicted_score', 'Not available')  # Replace with correct key
    explanation = model_response.get('explanation', 'Not available')  # Replace with correct key

    return predicted_engel_score, explanation
def prepare_training_data(csv_file):
    """
    Loads training data from a CSV file and prepares it for fine-tuning.
    :param csv_file: Path to the CSV file containing training data.
    :return: List of training examples.
    """
    data = pd.read_csv(csv_file)
    training_data = []
    for _, row in data.iterrows():
        clinical_note = row['clinical_note']
        engel_score = row['engel_score']
        reasoning = row['reasoning']
        
        prompt = f"Clinical Notes: {clinical_note}\n\nExplain the Engel score prediction."
        completion = f" Engel Score: {engel_score}. Reasoning: {reasoning}"
        
        training_data.append({
            "prompt": prompt,
            "completion": completion
        })
    return training_data
# Replace with your actual API key

if __name__ == "__main__":
    # Prepare the training data from the CSV file
    training_data = prepare_training_data('data/engel_scores_output.csv')

    # Fine-tune the Gemini model using the prepared training data
    # Assuming you have a function to fine-tune the model with training data
    # fine_tune_model(training_data)

    # Replace with your actual API key
    API_KEY = "AIzaSyCwPO_wC8UjEgYa8Y_SW_rkqkGv6e58uf0"

    # Example clinical notes
    clinical_notes = "Patient experiences frequent focal seizures, underwent temporal lobectomy, and has shown reduced seizure frequency post-surgery."
    engel_score_output = engel_score_pipeline(clinical_notes, API_KEY)
    print("Predicted Engel Score and Explanation:", engel_score_output)