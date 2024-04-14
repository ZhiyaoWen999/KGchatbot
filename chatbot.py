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
                program_name = entities.get("program_name", "")
                result = session.run(
                    "MATCH (p:Program {name: $program_name}) "
                    "RETURN p.description AS description, p.url AS url",
                    {"program_name": program_name}
                )
                record = result.single()
                if record:
                    return f"Program Details:\nDescription: {record['description']}\nURL: {record['url']}"
                else:
                    return "I couldn't find details for that program."

            elif intent == "course_details":
                course_name = entities.get("course_name", "")
                result = session.run(
                    "MATCH (c:Course {name: $course_name}) "
                    "RETURN c.name AS name",
                    {"course_name": course_name}
                )
                record = result.single()
                if record:
                    return f"Course Details: {record['name']}"
                else:
                    return "I couldn't find details for that course."

            elif intent == "requirements":
                program_name = entities.get("program_name", "")
                print(f"Looking up requirements for: {program_name}")
                result = session.run(
                    "MATCH (p:Program {name: $program_name})-[:HAS_REQUIREMENT]->(r:Requirement) "
                    "RETURN r.description AS description",
                    {"program_name": program_name}
                )
                
                records = result.data()
                
                print(f"Fetched records: {records}")

                if records:
                    requirements = '\n'.join(record['description'] for record in records)
                    return f"Requirements for {program_name}:\n{requirements}"
                else:
                    return "I couldn't find requirements for that program."

            else:
                return "I'm not sure how to help with that."
            


    def generate_response(self, user_input):
        try:
            intent, entities = self.parse_intent_and_entities(user_input)
            if not intent:
                return "I'm sorry, I didn't understand that. Can you please rephrase?"
            data = self.query_neo4j(self.construct_query(intent, entities))
            return self.format_response(data, intent)
        except openai.error.RateLimitError:
            return "I'm currently experiencing high demand. Please try again later."
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return "An error occurred. Please try again."
        
    def parse_intent_and_entities(self, text):
        intent = None  # Initialize intent and entities to None
        entities = {}
        try:
            # Using the chat completions endpoint for a chat model
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Parse the following user input into intent and entities. only map the intent to program_details, course_details, or requirements"},
                          {"role": "user", "content": text}]
            )
            content = response['choices'][0]['message']['content'].lower()

            # print("response**************", response)
            # print("content**************", content)
            if "program_details" in content:
                intent = "program_details"
                program_name = text.split("about")[-1].strip()
                entities = {"program_name": program_name}
            elif "course_details" in content:
                intent = "course_details"
                course_name = text.split("about")[-1].strip()
                entities = {"course_name": course_name}
            elif "requirements" in content:
                intent = "requirements"
                program_name = text.split("for")[-1].strip()
                entities = {"program_name": program_name}
                print(program_name)
            else:
                intent = "unknown"
                entities = {}

            return intent, entities
        except openai.error.InvalidRequestError as e:
            logging.error(f"API request error: {e}")
            return None, {}
        except openai.error.OpenAIError as e: 
            logging.error(f"An error occurred: {e}")
            return None, {}

    def construct_query(self, intent, entities):
        if intent == "program_details":
            return f"""
            MATCH (p:Program {{name: '{entities['program_name']}'}})
            OPTIONAL MATCH (p)-[:HAS_REQUIREMENT]->(r)
            OPTIONAL MATCH (p)-[:OFFERS_COURSE]->(c)
            RETURN p.description AS description, collect(r.description) AS requirements, collect(c.name) AS courses
            """
        else:
            return ""

    def format_response(self, data, intent):
        if not data:
            return "Sorry, I couldn't find information on that topic."
        if intent == "program_details":
            description = data[0]['description']
            requirements = ", ".join(data[0]['requirements'])
            courses = ", ".join(data[0]['courses'])
            return f"Program Description: {description}\nRequirements: {requirements}\nCourses: {courses}"
        else:
            return "Sorry, I couldn't understand your request."
        
    def run_chat_session(self):
        print("Welcome to the UCL Program Chatbot. Ask me about any program!")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Chatbot: Goodbye!")
                break
            response = self.generate_response(user_input)
            print("Chatbot:", response)

if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"
    openai.api_key = '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'  

    chatbot = Chatbot(openai.api_key, uri, user, password)
    try:
        
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break
            intent, entities = chatbot.parse_intent_and_entities(user_input)
            answer = chatbot.query_neo4j(intent, entities) if intent else "Sorry, I didn't understand that."
            print("Bot:", answer)
    finally:
        chatbot.close()




