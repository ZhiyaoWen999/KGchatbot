from neo4j import GraphDatabase

class QueryHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_courses_for_program(self, program_name):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Program {name: $program_name})
                -[:OFFERS_COURSE]->(c:Course)
                RETURN c.name AS course_name
            """, program_name=program_name)
            return [record["course_name"] for record in result]

    def get_requirements_for_course(self, course_name):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Course {name: $course_name})
                -[:REQUIRES]->(r:Requirement)
                RETURN r.description AS requirement
            """, course_name=course_name)
            return [record["requirement"] for record in result]

# Example usage:
uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

query_handler = QueryHandler(uri, user, password)
courses = query_handler.get_courses_for_program("Applied Paediatric Neuropsychology MSc")
requirements = query_handler.get_requirements_for_course("Some Course Name")

print("Courses:", courses)
print("Requirements:", requirements)

query_handler.close()