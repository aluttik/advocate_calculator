from py2neo import Graph, Node, Relationship
from sys import argv
import os

# constructs the neo4j Graph object
neo4j_username = os.environ["NEO4J_USERNAME"]
neo4j_password = os.environ["NEO4J_PASSWORD"]
auth = "%s:%s" % (neo4j_username, neo4j_password)
uri = "http://%s@localhost:7474/db/data" % auth
graph = Graph(uri)

def create_company_node(name, tw=None, em=None, fb=None):
    """ Creates a company type node

        Parameters: Name, Twitter Handle, Email Address, Facebook URL
        Returns: Company Node
    """
    properties = {"name" : name}
    properties["facebook"] = [fb] if fb else []
    properties["twitter"] = [tw] if tw else []
    properties["email"] = [em] if em else []
    company = Node.cast("company", properties)

    # searches for company nodes with the same name
    results = list(graph.find("company", "name", name))
    if results:
        # if there are already nodes of the same name in the graph,
        # add the information from the incoming node to the duplicate
        dupe = results[0]
        if fb and not fb in dupe["facebook"]: dupe["facebook"].append(fb)
        if tw and not tw in dupe["twitter"]: dupe["twitter"].append(tw)
        if em and not em in dupe["email"]: dupe["email"].append(em)
        dupe.push()
    else:
        # if there are no nodes of the same name in the graph,
        # add the company node to the graph as it is
        graph.create(company)


if __name__ == '__main__':
    # uses commandline arguments to create a company node for testing
    while len(argv) < 5: argv.append(None)
    create_company_node(argv[1], tw=argv[2], em=argv[3], fb=argv[4])

    # prints the current state of the graph on finish
    print graph.cypher.execute('MATCH (n) RETURN n')

