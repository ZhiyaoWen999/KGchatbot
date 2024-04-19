import openai
from neo4j import GraphDatabase
import logging

class Chatbot:
    def __init__(self, openai_api_key, neo4j_uri, neo4j_user, neo4j_password):
        self.openai_api_key = openai_api_key
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        logging.basicConfig(level=logging.INFO)

    def close(self):
        self.driver.close()

    def query_neo4j(self, intent, entities):
        with self.driver.session() as session:
            if intent == "program_details":
                return self.fetch_program_details(session, entities.get("program_name"))
            elif intent == "course_details":
                return self.fetch_course_details(session, entities.get("course_name"))
            elif intent == "requirements":
                return self.fetch_requirements(session, entities.get("program_name"))
            return "I'm not sure how to help with that."

    def fetch_program_details(self, session, program_name):
        result = session.run("MATCH (p:Program {name: $program_name}) RETURN p.description AS description, p.url AS url", {"program_name": program_name})
        record = result.single()
        if record:
            return f"Program Details:\nDescription: {record['description']}\nURL: {record['url']}"
        return "I couldn't find details for that program."

    def fetch_course_details(self, session, course_name):
        result = session.run("MATCH (c:Course) WHERE c.name CONTAINS $course_name RETURN c.name AS name, c.description AS description", {"course_name": course_name})
        record = result.single()
        if record:
            return f"Course Details: {record['name']} {record['description']}"
        return "I couldn't find details for that course."

    def fetch_requirements(self, session, program_name):
        result = session.run("MATCH (p:Program {name: $program_name})-[:HAS_REQUIREMENT]->(r:Requirement) RETURN r.description AS description", {"program_name": program_name})
        records = result.data()
        if records:
            requirements = '\n'.join(record['description'] for record in records)
            return f"Requirements for {program_name}:\n{requirements}"
        return "I couldn't find requirements for that program."

    def parse_intent_and_entities(self, text):
        openai.api_key = self.openai_api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Parse the following user input into intent and entities. only map the intent to program_details, course_details, or requirements and do not break the course name"},
                      {"role": "user", "content": text}]
        )
        content = response['choices'][0]['message']['content'].lower()
        # print(content)
        if "program_details" in content:
            
            program_name = text.split("about")[-1].strip(' ?')
            print(f"Looking up program details for: {program_name}")

            return "program_details", {"program_name": program_name}
        if "course_details" in content:
            
            course_name = text.split("about")[-1].strip(' ?')
            print(f"Looking up course details for: {course_name}")

            return "course_details", {"course_name": course_name}
        if "requirements" in content:
            
            program_name = text.split("for")[-1].strip(' ?')
            print(f"Looking up requirements for: {program_name}")

            return "requirements", {"program_name": program_name}
        return None, {}

    def run_chat_session(self):
        print("Welcome to the UCL Program Chatbot. Ask me about any program!")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Chatbot: Goodbye!")
                break
            intent, entities = self.parse_intent_and_entities(user_input)
            if intent:
                answer = self.query_neo4j(intent, entities)
            else:
                answer = "Sorry, I didn't understand that."
            print("Chatbot:", answer)

if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"
    openai_api_key = '' # Set your OpenAI API key here

    chatbot = Chatbot(openai_api_key, uri, user, password)
    try:
        chatbot.run_chat_session()
    finally:
        chatbot.close()

