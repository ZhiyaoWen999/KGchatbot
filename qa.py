from neo4j import GraphDatabase
import json

class KnowledgeGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_program(self, program_name, program_info):
        with self.driver.session() as session:
            session.write_transaction(self._create_program_node, program_name, program_info)

    @staticmethod
    def _create_program_node(tx, program_name, program_info):
        # Convert complex information to string or multiple properties
        query = (
            "MERGE (p:Program {name: $program_name}) "
            "SET p.url = $url, p.description = $description "
            "RETURN p"
        )
        tx.run(query, program_name=program_name, url=program_info['URL'], description=program_info['Description'])

    def create_relationship(self, program_name, content, content_type):
        with self.driver.session() as session:
            session.write_transaction(self._create_relationship, program_name, content, content_type)

    @staticmethod
    def _create_relationship(tx, program_name, content, content_type):
        query = (
            "MATCH (p:Program {name: $program_name}) "
            f"MERGE (c:{content_type} {{content: $content}}) "
            f"MERGE (p)-[:HAS_{content_type.upper()}]->(c)"
        )
        tx.run(query, program_name=program_name, content=content)

def main():
    # Load your transformed JSON data
    with open('data/transformed_course_info.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Initialize your connection to Neo4j (replace with your credentials)
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"  # Change this to your Neo4j password
    kg_builder = KnowledgeGraphBuilder(uri, user, password)

    # Create nodes and relationships
    for course in data:
        # Here, program_info is expected to be a dictionary with 'URL' and 'Description' keys
        kg_builder.create_program(course['Program'], course)
        for requirement in course['Requirements'].split(". "):
            if requirement:  # Ensure the requirement is not empty
                kg_builder.create_relationship(course['Program'], requirement, "Requirement")
        for course_detail in course['Courses'].split(". "):
            if course_detail:  # Ensure the course detail is not empty
                kg_builder.create_relationship(course['Program'], course_detail, "Course")

    kg_builder.close()

if __name__ == "__main__":
    main()
