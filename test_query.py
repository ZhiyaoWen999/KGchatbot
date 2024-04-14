from neo4j import GraphDatabase

class QueryHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_courses_for_program(self, program_name):
        with self.driver.session() as session:
            return self._fetch_courses(session, program_name)

    def get_requirements_for_course(self, course_name):
        with self.driver.session() as session:
            return self._fetch_requirements(session, course_name)

    def get_program_details(self, program_name):
        courses = self.get_courses_for_program(program_name)
        requirements = [self.get_requirements_for_course(course) for course in courses]
        return {
            "Program": program_name,
            "Courses": courses,
            "Requirements": requirements
        }

    def _fetch_courses(self, session, program_name):
        result = session.run("""
            MATCH (p:Program {name: $program_name})-[:OFFERS_COURSE]->(c:Course)
            RETURN c.name AS course_name
        """, program_name=program_name)
        return [record["course_name"] for record in result]

    def _fetch_requirements(self, session, course_name):
        result = session.run("""
            MATCH (c:Course {name: $course_name})-[:REQUIRES]->(r:Requirement)
            RETURN r.description AS requirement
        """, course_name=course_name)
        return [record["requirement"] for record in result]


if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"
    query_handler = QueryHandler(uri, user, password)

    program_name = "Applied Paediatric Neuropsychology MSc"
    program_details = query_handler.get_program_details(program_name)
    print("Program Details:", program_details)

    query_handler.close()


