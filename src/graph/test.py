from neo4j import GraphDatabase

NEO4J_URI = "neo4j+s://a3ccaeb7.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "TzR6rQkvmPBm25_LJcd9AIclvx4sgH4z9mKqfbQVqXI"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

try:
   with driver.session() as session:
       result = session.run("RETURN 1")  # Simple test query
       print(result.single())
except Exception as e:
   print(f"Error: {e}")
finally:
   driver.close()