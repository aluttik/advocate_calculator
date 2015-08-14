from py2neo import Graph, Node, Relationship
import os
import sys

neo4j_username = os.environ["NEO4J_USERNAME"]
neo4j_password = os.environ["NEO4J_PASSWORD"]

graph = Graph("http://" + neo4j_username + ":" + neo4j_password + "@localhost:7474/db/data/")

def create_company_node(nm, tw=None, em=None, fb=None):
    """ Creates a comany type node

        Parameters: Name, Twitter Handle, Email Address, Facebook URL
        Returns: Company Node
    """
    tw_accs = []
    em_accs = []
    fb_accs = []
    if tw: tw_accs.append(tw)
    if em: em_accs.append(em)
    if fb: fb_accs.append(fb)
    company = Node("Company", name=nm, twitter=tw_accs, email=em_accs, facebook=fb_accs)

    results = list(graph.find("Company", "name", nm))
    if results:
        comp = results[0]
        print "node in db (outdated):", comp.properties
        if tw and not tw in comp["twitter"]: comp["twitter"].append(tw)
        if em and not em in comp["email"]: comp["email"].append(em)
        if fb and not fb in comp["facebook"]: comp["facebook"].append(fb)
        print "node in db (merged):", comp.properties
        comp.push()
    else:
        graph.create(company)
        print "local node:", company.properties


if __name__ == '__main__':
    create_company_node("test", tw=sys.argv[1])
