from py2neo import Graph, Node, Relationship
import os

neo4j_username = os.environ["NEO4J_USERNAME"]
neo4j_password = os.environ["NEO4J_PASSWORD"]

graph = Graph("http://" + neo4j_username + ":" + neo4j_password + "@localhost:7474/db/data/")

def create_company_node(name, twitter=None, email=None, fb=None):
    """ Creates a comany type node

        Parameters: Name, Twitter Handle, Email Address, Facebook URL
        Returns: Company Node
    """

    company = Node("Company", name=name)
    if twitter: company.properties["twitter"] = twitter
    if email: company.properties["email"] = email
    if fb: company.properties['fb'] = fb
    return company

if __name__ == '__main__':
    test_company = create_company_node("shannonland", twitter="yotweet")
    graph.create(test_company)
