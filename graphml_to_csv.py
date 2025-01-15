import lxml.etree as etree
import pandas as pd 

GRAPHML_NS = {'graphml': 'http://graphml.graphdrawing.org/xmlns',
              'y': 'http://www.yworks.com/xml/graphml'}

# Parse the document
doc = etree.parse("conceptual_model.graphml")

# Use the namespace in xpath
edges = doc.xpath(".//graphml:edge", namespaces=GRAPHML_NS) # getting list of all edges in the XML with xpath query 
nodes = doc.xpath(".//graphml:node", namespaces=GRAPHML_NS) # gettin list of all nodes 
node_dict = {node.get("id"):node for node in nodes} # organizing each node in a dict, using their respective ID

# We are building a list of dictionaries with 3 keys (s, p, o) structure
triples = []
for edge in edges: 
    # getting the edge label value, where possible
    try:
        p = edge.find(".//y:EdgeLabel", namespaces=GRAPHML_NS).text 
    except:
        print("Some edges appear to be unlabeld. Check the output for missing values under the 'Predicate' column")
    #getting te IDs of the two nodes linked by the edge
    s_id = edge.get("source") 
    t_id = edge.get("target")
    # getting the node elements from the dict
    source = node_dict[s_id]
    target = node_dict[t_id]
    #retrieving all the labels of source and target nodes of each edge
    s_list = source.findall(".//y:NodeLabel", namespaces=GRAPHML_NS) 
    o_list = target.findall(".//y:NodeLabel", namespaces=GRAPHML_NS)
    for s_el, o_el in zip(s_list, o_list): # looping on the two lists
        sub_content = s_el.text
        obj_content = o_el.text
        # checking if the elements are empty or whitespace strings
        s = sub_content if sub_content.strip() else None
        o = obj_content if obj_content.strip() else None
    triples.append({
        "subject":s,
        "Predicate":p,
        "Object":o
    })

df = pd.DataFrame(triples)
df.to_csv(path_or_buf="graph_data.csv", index=False)