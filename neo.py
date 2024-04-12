from neo4j import GraphDatabase

class KnowledgeGraphBuilder:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_course(self, course_info):
        with self.driver.session() as session:
            session.write_transaction(self._create_and_link, course_info)

    @staticmethod
    def _create_and_link(tx, course_info):
        # 创建课程节点
        course_node = tx.run("CREATE (c:Course {title: $title, url: $url}) RETURN c", course_info).single()["c"]
        # 创建描述节点并与课程节点链接
        tx.run("CREATE (d:Description {text: $description}) "
               "CREATE (c)-[:DESCRIBED_BY]->(d)", 
               dict(course_info, **{"description": course_info["description"]}))
        # 对于每个内容段落，创建内容节点并与课程节点链接
        for paragraph in course_info["contents"]:
            tx.run("CREATE (p:Content {text: $text}) "
                   "CREATE (c)-[:CONTAINS]->(p)", 
                   dict(course_info, **{"text": paragraph}))

# 使用实例
kg_builder = KnowledgeGraphBuilder("bolt://localhost:7687", "neo4j", "12345678")

# 假设您已经从先前的步骤中提取了这些信息
course_info_example = {
    "title": "Geophysical Hazards MSc",
    "url": "https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees/geophysical-hazards-msc",
    "description": "This programme provides students with detailed knowledge...",
    "contents": ["Content paragraph 1...", "Content paragraph 2..."]
}

kg_builder.create_course(course_info_example)

kg_builder.close()

