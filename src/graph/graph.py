from neo4j import GraphDatabase
from named_entity_recognition import execute_ner
import os
import time 


def convert_entities(entities: dict):
    queries = []
    for label, entity_list in entities.items():
        for entity in entity_list:
            # Use the entity name as the unique identifier
            query = f"CREATE (:{label} {{name: $name}})"
            params = {"name": entity}
            queries.append((query, params))
    return queries

def convert_relations(relations: list):
    queries = []
    for rel in relations:
        source = rel["source"]
        target = rel["target"]
        rel_type = rel["type"]

        query = f"""
            MATCH (from {{ name: $source }}), (to {{ name: $target }})
            CREATE (from)-[:{rel_type}]->(to)
        """
        params = {"source": source, "target": target}
        queries.append((query, params))
    return queries

def execute_query(uri: str, username: str, password, queries: list):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        with driver.session() as session:
            for query, params in queries:
                session.run(query, params)
    finally:
        driver.close()

def upload(uri: str, username: str, password: str, data: dict):
    
    # Extracting entities and relations from the data
    entity_queries = convert_entities(data["Entities"])
    relation_queries = convert_relations(data["Relations"])

    # Execute queries
    execute_query(uri, username, password, entity_queries)
    execute_query(uri, username, password, relation_queries)

def build_graph(uri: str, username: str, password: str):
    
    # open all of clinical notes, read the file, and process with ner
   
    count = 175
    for clinical_note_filename in os.listdir('data/clinical_notes')[183:]:
      
        # Construct clinical note path
        clinical_note_path = os.path.join('data/clinical_notes', clinical_note_filename)

        # Read the clinical note text
        with open(clinical_note_path, 'r') as clinical_note_file:
            clinical_note_text = clinical_note_file.read()
            
            # Execute NER on the clinical note text

            ner = execute_ner(clinical_note_text)
            
            upload(uri, username, password, ner)
            
            print(f"Graph created for {clinical_note_filename}")
            print(f"Processed {count} files")
            count += 1
            time.sleep(12)

# do not run unless you want to re-learn the knowledge graph
#build_graph(os.getenv(NEO4J_URI), os.getenv(NEO4J_USERNAME), os.getenv(NEO4J_PASSWORD))
