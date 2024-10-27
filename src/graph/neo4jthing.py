from neo4j import GraphDatabase

class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_node(self, label, properties):
        try:
            with self.driver.session() as session:
                session.write_transaction(self._create_node, label, properties)
        except Exception as e:
            print(f"Error creating node: {e}")

    @staticmethod
    def _create_node(tx, label, properties):
        query = f"CREATE (n:{label} $properties)"
        tx.run(query, properties=properties)

    def create_relationship(self, start_node_label, start_node_id, end_node_label, end_node_id, relationship_type):
        try:
            with self.driver.session() as session:
                session.write_transaction(self._create_relationship, start_node_label, start_node_id, end_node_label, end_node_id, relationship_type)
        except Exception as e:
            print(f"Error creating relationship: {e}")

    @staticmethod
    def _create_relationship(tx, start_node_label, start_node_id, end_node_label, end_node_id, relationship_type):
        query = f"""
        MATCH (a:{start_node_label}),(b:{end_node_label})
        WHERE a.id = $start_node_id AND b.id = $end_node_id
        CREATE (a)-[r:{relationship_type}]->(b)
        RETURN type(r)
        """
        tx.run(query, start_node_id=start_node_id, end_node_id=end_node_id)

# Example usage
if __name__ == "__main__":
    uri = "neo4j+s://8726e09d.databases.neo4j.io"  # Ensure this is correct
    user = "neo4j"  # Confirm this
    password = "hGXErMhwOXlihaWz4OwywjWnhO0UmwVgBEc9Fo0tAM"  # Confirm this

    neo4j_handler = Neo4jHandler(uri, user, password)

    # Create nodes
    neo4j_handler.create_node("Patient", {"id": 1, "name": "John Doe", "age": 30})
    neo4j_handler.create_node("Diagnosis", {"id": 101, "type": "Epilepsy", "severity": "Moderate"})

    # Create relationship
    neo4j_handler.create_relationship("Patient", 1, "Diagnosis", 101, "HAS_DIAGNOSIS")

    # Close the connection
    neo4j_handler.close()

