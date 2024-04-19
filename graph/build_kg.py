from neo4j import GraphDatabase
import json
import logging

class KnowledgeGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logging.basicConfig(level=logging.INFO)

    def close(self):
        if self.driver:
            self.driver.close()

    def load_data(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data

    def create_graph(self, data):
        # Batch processing
        batch_size = 100
        batches = [data[i:i + batch_size] for i in range(0, len(data), batch_size)]
        for batch in batches:
            with self.driver.session() as session:
                for course in batch:
                    self.create_program(session, course)
                    self.create_requirements(session, course)
                    self.create_courses(session, course)
                    self.create_topics(session, course)
                    self.link_course_requirements(session, course)
            logging.info(f"Processed a batch of {len(batch)} courses")

    def create_program(self, session, course):
        logging.info(f"Creating program node for: {course['Program']}")
        program_query = """
        MERGE (p:Program {name: $name})
        ON CREATE SET p.url = $url, p.description = $description
        RETURN p
        """
        program_attributes = {
            'name': course['Program'],
            'url': course['URL'],
            'description': course['CleanedDescription']
        }
        session.run(program_query, program_attributes)

    def create_requirements(self, session, course):
        logging.info(f"Creating requirement nodes for: {course['Program']}")
        requirements_query = """
        MATCH (p:Program {name: $programName})
        UNWIND $requirements AS reqDescription
        MERGE (r:Requirement {description: reqDescription})
        MERGE (p)-[:HAS_REQUIREMENT]->(r)
        """
        session.run(requirements_query, programName=course['Program'], requirements=course['Requirements'])

    def create_courses(self, session, course):
        logging.info(f"Creating course nodes for: {course['Program']}")
        courses_query = """
        MATCH (p:Program {name: $programName})
        UNWIND $courses AS courseName
        MERGE (c:Course {name: courseName})
        MERGE (p)-[:OFFERS_COURSE]->(c)
        """
        session.run(courses_query, programName=course['Program'], courses=course['Courses'])

    def create_topics(self, session, course):
        logging.info(f"Creating topic nodes for courses in: {course['Program']}")
        topics_query = """
        UNWIND $courses AS courseDetail
        UNWIND $topics AS topicName
        MATCH (c:Course {name: courseDetail})
        MERGE (k:Topic {name: topicName})
        MERGE (c)-[:COVERS_TOPIC]->(k)
        """
        session.run(topics_query, courses=course['Courses'], topics=course.get('KeyTopics', []))

    def link_course_requirements(self, session, course):
        logging.info(f"Linking courses to requirements for: {course['Program']}")
        link_query = """
        UNWIND $courses AS courseDetail
        UNWIND $requirements AS reqDescription
        MATCH (c:Course {name: courseDetail})
        MATCH (r:Requirement {description: reqDescription})
        MERGE (c)-[:REQUIRES]->(r)
        """
        session.run(link_query, courses=course['Courses'], requirements=course['Requirements'])

if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"
    filepath = 'data/cleaned_data/cleaned_course_info.json' 

    kg_builder = KnowledgeGraphBuilder(uri, user, password)
    course_data = kg_builder.load_data(filepath)
    kg_builder.create_graph(course_data)
    kg_builder.close()
