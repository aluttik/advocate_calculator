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
        print len(results)
        comp = results[0]
        print "Do I have properties?", comp.properties
        #add current props to list
        # tw_accs.extend([comp["twitter"], tw])
        # em_accs.extend([comp["email"], em])
        # fb_accs.extend([comp["facebook"], fb])
        #rewrite properties as lists
        print comp["twitter"]
        comp["twitter"].extend(tw_accs)
        comp["email"].extend(em_accs)
        comp["facebook"].extend(fb_accs)
        print "Do I have properties?", comp.properties

        print "remote: I am bound?", comp.bound
        comp.push()
    else:
        graph.create(company)
        print "company.properties:", company.properties
    # if company.exists() != True:
    #     return company


if __name__ == '__main__':
    test_company = create_company_node("ted", tw=sys.argv[1], em="bloop")
