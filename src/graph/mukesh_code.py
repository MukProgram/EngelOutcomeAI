from neo4j import GraphDatabase
import json

def convert_nodes(nodes: dict):
    queries = []
    for label, node_list in nodes.items():
        for node in node_list:
            properties = ', '.join(f"{k}: ${k}_{node['_uid']}" for k in node.keys())
            query = f"CREATE (:{label} {{{properties}}})"
            queries.append((query, {f"{k}_{node['_uid']}": v for k, v in node.items()}))
    return queries

def convert_relationships(relationships: dict):
    queries = []
    for rel_type, rel_records in relationships.items():
        for record in rel_records:
            from_uid = record["_from__uid"]
            to_uid = record["_to__uid"]
            properties = ', '.join(f"{k}: ${k}_{record['_uid']}" for k in record.keys() if k not in {'_from__uid', '_to__uid'})
            query = f"""
                MATCH (from {{ _uid: {from_uid} }}), (to {{ _uid: {to_uid} }})
                CREATE (from)-[:{rel_type} {{{properties}}}]->(to)
            """
            queries.append((query, {f"{k}_{record['_uid']}": v for k, v in record.items()}))
    return queries

def execute_query(uri: str, username: str, password: str, queries: list):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        with driver.session() as session:
            for query, params in queries:
                session.run(query, params)
    finally:
        driver.close()

def upload(uri: str, username: str, password: str, data: dict):
    nodes_queries = convert_nodes(data["nodes"])
    rel_queries = convert_relationships(data["relationships"])

    execute_query(uri, username, password, nodes_queries)
    execute_query(uri, username, password, rel_queries)

if __name__ == "__main__":
    data = {
        "nodes": {
            "Patient": [
                {"_uid": 1, "name": "John Doe"},
                {"_uid": 2, "name": "Jane Smith"}
            ],
            "Diagnosis": [
                {"_uid": 3, "name": "Epilepsy"},
                {"_uid": 4, "name": "Temporal Lobe Epilepsy"}
            ]
        },
        "relationships": {
            "HAS": [
                {"_uid": 5, "_from__uid": 1, "_to__uid": 3},
                {"_uid": 6, "_from__uid": 2, "_to__uid": 4}
            ]
        }
    }

    uri = "neo4j+s://a3ccaeb7.databases.neo4j.io"
    username = "neo4j"
    password = "TzR6rQkvmPBm25_LJcd9AIclvx4sgH4z9mKqfbQVqXI"

    upload(uri, username, password, data)
