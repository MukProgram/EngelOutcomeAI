import os
import requests
import pandas as pd
from neo4j import GraphDatabase
import logging
from named_entity_recognition import execute_ner 

neo4j_uri = os.getenv('NEO4J_URI')
neo4j_user = os.getenv('NEO4J_USER')
neo4j_password = os.getenv('NEO4J_PASSWORD')
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

logger = logging.getLogger(__name__)

def extract_entity_names(clinical_entities_dict):
    """
    Extracts a list of unique entity names from the clinical_entities dictionary.
    
    :param clinical_entities_dict: Dictionary containing entity types and their corresponding entities.
    :return: List of unique entity names.
    """
    entity_names = []
    entities = clinical_entities_dict.get("Entities", {})
    for entity_type, entities_list in entities.items():
        entity_names.extend(entities_list)
    unique_entity_names = list(set(entity_names))
    return unique_entity_names

def retrieve_knowledge_graph_context(entity_names, limit_per_entity=5):
    """
    Queries the knowledge graph to find related entities based on a list of entity names.
    
    :param entity_names: List of entity names to search in the knowledge graph.
    :param limit_per_entity: Maximum number of relationships to retrieve per entity.
    :return: List of retrieved data.
    """
    if not entity_names:
        logger.warning("No entity names provided for knowledge graph retrieval.")
        return []
    
    query = """
    MATCH (n)-[r]->(m)
    WHERE ANY(entity IN $entity_names WHERE 
        n.name = entity OR m.name = entity)
    RETURN n.name AS Entity1, 
           labels(n) AS Entity1Labels, 
           type(r) AS Relationship, 
           m.name AS Entity2, 
           labels(m) AS Entity2Labels
    ORDER BY Entity1, Relationship
    """
    
    logger.debug(f"Executing Query: {query}")
    logger.debug(f"With Parameters: entity_names={entity_names}")
    
    try:
        with driver.session() as session:
            result = session.run(query, entity_names=entity_names)
            data = []
            from collections import defaultdict
            relationships_per_entity = defaultdict(int)
            
            for record in result:
                entity = record["Entity1"]
                if relationships_per_entity[entity] < limit_per_entity:
                    data.append({
                        "Entity1": record["Entity1"],
                        "Entity1Labels": record["Entity1Labels"],
                        "Relationship": record["Relationship"],
                        "Entity2": record["Entity2"],
                        "Entity2Labels": record["Entity2Labels"]
                    })
                    relationships_per_entity[entity] += 1
            
            logger.info(f"Retrieved {len(data)} related entries from the knowledge graph.")
            logger.info(f"Knowledge Graph Data: {data}")
            return data
    except Exception as e:
        logger.error(f"Error querying knowledge graph: {e}")
        return []

def prepare_input_for_gemini(clinical_notes, entity_names, knowledge_graph_data):
    
    """
    Prepares the input for the Gemini API by combining clinical notes and knowledge graph context.
    
    :param clinical_notes: Raw clinical notes text.
    :param entity_names: List of extracted entity names.
    :param knowledge_graph_data: Retrieved knowledge graph context.
    :return: Formatted prompt for Gemini.
    """
    
    # Format knowledge graph data into context text
    context_text = "\n".join([
        f"{data['Entity1']} ({data['Relationship']}) {data['Entity2']} [Label1: {', '.join(data['Entity1Labels']), ', '.join(data['Entity2Labels'])}]"
        for data in knowledge_graph_data
    ])
    
    # Format clinical entities for better readability
    entities_text = ", ".join(entity_names)
    
    prompt = f"""
    Please review the clinical note provided below and assess the patient using the Engel Outcome Scale criteria listed afterward. Assign an Engel score (number and letter) to the patient, even if certain aspects of the criteria are unclear or missing. For this task, ignore whether or not the patient is post-surgery. If and only if there are multiple possible scores with valid reasoning, provide all possible scores and their reasoning as a list.

**Engel Outcome Scale**
Class I: Free of disabling seizures
IA: Completely seizure-free since surgery
IB: Non-disabling simple partial seizures only since surgery
IC: Some disabling seizures after surgery, but free of disabling seizures for at least 2 years
ID: Generalized convulsions with antiepileptic drug withdrawal only

Class II: Rare disabling seizures (“almost seizure-free”)
IIA: Initially free of disabling seizures but has rare seizures now
IIB: Rare disabling seizures since surgery
IIC: More than rare disabling seizures after surgery, but rare seizures for at least 2 years
IID: Nocturnal seizures only

Class III: Worthwhile improvement
IIIA: Worthwhile seizure reduction
IIIB: Prolonged seizure-free intervals amounting to greater than half the follow-up period, but not less than 2 years

Class IV: No worthwhile improvement
IVA: Significant seizure reduction
IVB: No appreciable change
IVC: Seizures worse

**Raw Clinical Note**:
{clinical_notes}

**Extracted Clinical Entities**: {entities_text}

**Context from Knowledge Graph**:
{context_text}

**Output Requirements:**
1. **Engel Score**: Provide the score as a number and letter (e.g., "1A").
2. **Reasoning**: Write a thorough explanation for the chosen score, detailing the clinical reasoning behind your decision.
3. **Variations** If and only if there are multiple possible scores with valid reasoning, provide all possible scores and their reasoning as a list.

Return the results in JSON format, structured as follows:
```json
{{
  "score": "<Engel Score>",
  "reasoning": "<Detailed clinical reasoning>"
}}
"""
    logger.debug(f"Prepared Prompt: {prompt}")
    return prompt

def engel_score_pipeline(clinical_note, limit=5):
    """
    Pipeline to predict Engel score based on clinical notes and knowledge graph context.
    
    :param clinical_notes: Raw clinical notes text.
    :param limit: Maximum number of relationships to retrieve per entity.
    :return: Predicted Engel score and explanation.
    """
    
    clinical_entities = execute_ner(clinical_note)
    logger.info(f"Extracted entities: {clinical_entities}")
    
    entity_names = extract_entity_names(clinical_entities)
    logger.info(f"Entity Names for Querying: {entity_names}")
    
    knowledge_graph_data = retrieve_knowledge_graph_context(entity_names, limit_per_entity=limit)
    
    if not knowledge_graph_data:
        logger.warning("No knowledge graph data retrieved. Proceeding without additional context.")
    
    augmented_prompt = prepare_input_for_gemini(clinical_note, entity_names, knowledge_graph_data)
    return augmented_prompt

