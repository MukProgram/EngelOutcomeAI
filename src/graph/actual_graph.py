from neo4j import GraphDatabase

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

def upload(uri, username, password, data):
    # Extracting entities and relations from the data
    entity_queries = convert_entities(data["Entities"])
    relation_queries = convert_relations(data["Relations"])

    # Execute queries
    execute_query(uri, username, password, entity_queries)
    execute_query(uri, username, password, relation_queries)

if __name__ == "__main__":
    data = {
        "Entities": {
            "PastDiagnoses": ["probable generalized epilepsy"],
            "Age": ["50-year-old"],
            "FrequencyOfSeizures": ["every two months"],
            "SeizureOnset": ["began in childhood", "reappeared five years ago"],
            "SeizureRelatedInjuries": ["injured herself", "bit her tongue"],
            "MedicationHistory": ["sodium valproate", "levetiracetam"],
            "Patient": ["She"]
        },
        "Relations": [
            {"type": "HAS", "source": "She", "target": "probable generalized epilepsy"},
            {"type": "EXPERIENCES", "source": "She", "target": "bit her tongue"},
            {"type": "LEADS_TO", "source": "began in childhood", "target": "probable generalized epilepsy"}
        ]
    }

    uri = "neo4j+s://a3ccaeb7.databases.neo4j.io"
    username = "neo4j"
    password = "TzR6rQkvmPBm25_LJcd9AIclvx4sgH4z9mKqfbQVqXI"

    upload(uri, username, password, data)
