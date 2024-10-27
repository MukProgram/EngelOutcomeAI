import requests
import pandas as pd
from neo4j import GraphDatabase
import ssl


# Configuration
GEMINI_API_URL = "https://api.gemini.com/v1/embeddings"
NEO4J_URI = "neo4j+s://41ff287f.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "hhGXErMhwOXlihaWz4OwywjWnhO0UmwVgBEc9Fo0tAM"
CLINICAL_NOTES_FILE = "data/engel_scores_output.csv"  # CSV file with clinical notes

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password), database="neo4j")

    def close(self):
        self.driver.close()

    def create_node(self, label, properties):
        with self.driver.session() as session:
            session.run(f"CREATE (n:{label} $props", props=properties)  # Fix syntax error

    def create_relationship(self, from_label, from_id, to_label, to_id, rel_type):
        with self.driver.session() as session:
            session.run(
                f"MATCH (a:{from_label} {{id: $from_id}}), (b:{to_label} {{id: $to_id}}) "
                f"CREATE (a)-[:{rel_type}]->(b)",
                from_id=from_id, to_id=to_id
            )

def extract_entities(note):
    response = requests.post(
        GEMINI_API_URL,
        json={"text": note},
        headers={"Authorization": "YOUR_API_KEY"}
    )
    return response.json()

def get_embeddings(note):
    response = requests.post(
        GEMINI_API_URL,  # Use the same API URL here
        json={"text": note},
        headers={"Authorization": "YOUR_API_KEY"}
    )
    return response.json()

def main():
    # Initialize Neo4j connection
    neo4j_conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    # Read clinical notes from a CSV file
    clinical_notes_df = pd.read_csv(CLINICAL_NOTES_FILE)

    for index, row in clinical_notes_df.iterrows():
        note = row['clinical_note']  # Assuming the column name is 'clinical_note'
        score = row['engel_score']    # Assuming the column name is 'engel_score'
        reasoning = row['reasoning']   # Assuming the column name is 'reasoning'

        # Extract entities
        entities = extract_entities(note)

        # Get embeddings
        embeddings = get_embeddings(note)

        # Create patient node
        patient_properties = {
            "id": str(index),
            "note": note,
            "engel_score": score,
            "reasoning": reasoning,
            "embedding": embeddings.get("embedding")  # Assuming the embedding is returned in a certain format
        }
        neo4j_conn.create_node("Patient", patient_properties)

        # Create symptom nodes and relationships (as an example)
        for entity in entities.get("symptoms", []):
            symptom_properties = {
                "id": entity['id'],
                "name": entity['name'],
                "embedding": embeddings.get("embedding")  # Embedding for symptom
            }
            neo4j_conn.create_node("Symptom", symptom_properties)
            neo4j_conn.create_relationship("Patient", str(index), "Symptom", entity['id'], "HAS_SYMPTOM")

    # Close Neo4j connection
    neo4j_conn.close()

if __name__ == "__main__":
    main()
