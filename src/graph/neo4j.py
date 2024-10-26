from neo4j import GraphDatabase

class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_node(self, label, properties):
        with self.driver.session() as session:
            session.write_transaction(self._create_node, label, properties)

    @staticmethod
    def _create_node(tx, label, properties):
        query = f"CREATE (n:{label} $properties)"
        tx.run(query, properties=properties)

    def create_relationship(self, start_node_label, start_node_id, end_node_label, end_node_id, relationship_type):
        with self.driver.session() as session:
            session.write_transaction(self._create_relationship, start_node_label, start_node_id, end_node_label, end_node_id, relationship_type)

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
    uri = "bolt://localhost:7687"  # Change to your Neo4j URI
    user = "neo4j"                  # Change to your Neo4j username
    password = "password"            # Change to your Neo4j password

    neo4j_handler = Neo4jHandler(uri, user, password)

    # Create nodes
    neo4j_handler.create_node("Patient", {"id": 1, "name": "John Doe", "age": 30})
    neo4j_handler.create_node("Diagnosis", {"id": 101, "type": "Epilepsy", "severity": "Moderate"})

    # Create relationship
    neo4j_handler.create_relationship("Patient", 1, "Diagnosis", 101, "HAS_DIAGNOSIS")

    # Close the connection
    neo4j_handler.close()
