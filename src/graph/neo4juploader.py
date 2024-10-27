from neo4j import GraphDatabase
import json

def execute_query(uri: str, username: str, password: str, query: str, params: dict):
    with GraphDatabase.driver(uri, auth=(username, password)) as driver:
        # with driver.session() as session:
        #     result = session.run(query, params)
        #     return result.summary
        driver.verify_connectivity
        result = driver.execute_query(query, params)
        return result

def convert_nodes(nodes: dict):
    query = ""
    params = {}

    for node_label, node_records in nodes.items():
        for record in node_records:
            param_key = f'node_{record["_uid"]}'
            params[param_key] = record
            query += f"""CALL apoc.create.nodes(["{node_label}"], ${param_key});\n"""

    return query, params

def convert_relationships(relationships: dict):
    rel_record_list = []
    params = {}

    for rel_type, rel_records in relationships.items():
        for record in rel_records:
            record_key = str(record.get('_uid'))
            params[record_key] = record
            from_node_uid = str(record.get('_from__uid'))
            to_node_uid = str(record.get('_to__uid'))
            item = f"['{rel_type}', '${from_node_uid}', '${to_node_uid}', ${record_key}]"
            rel_record_list.append(item)

    composite_rel_records_list = ",".join(rel_record_list)

    query = f"""WITH [{composite_rel_records_list}] AS rel_data
                UNWIND rel_data AS relationship
                MATCH (n {{`_uid`:relationship[1]}})
                MATCH (n2 {{`_uid`:relationship[2]}})
                CALL apoc.create.relationship(n, relationship[0], relationship[3], n2) YIELD rel
                RETURN rel
    """

    return query, params

def upload(uri: str, username: str, password: str, data: str):
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception as e:
            raise Exception(f'Error converting data to json: {e}')

    node_query, node_params = convert_nodes(data['nodes'])
    execute_query(uri, username, password, node_query, node_params)

    rel_query, rel_params = convert_relationships(data['relationships'])
    execute_query(uri, username, password, rel_query, rel_params)

if __name__ == "__main__":
    uri = "neo4j+s://8726e09d.databases.neo4j.io"
    user = "neo4j"
    password = "hGXErMhwOXlihaWz4OwywjWnhO0UmwVgBEc9Fo0tAM"

    # Example data structure
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

    upload(uri, user, password, json.dumps(data))
