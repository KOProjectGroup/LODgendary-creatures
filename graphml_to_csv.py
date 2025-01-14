import regex
import lxml
import lxml.etree as etree
import pandas as pd 
import csv

GRAPHML_NS = {'graphml': 'http://graphml.graphdrawing.org/xmlns',
              'y': 'http://www.yworks.com/xml/graphml'}

# Parse the document
doc = etree.parse("conceptual/cm_v.graphml")

# Use the namespace in xpath
edges = doc.xpath(".//graphml:edge", namespaces=GRAPHML_NS)
nodes = doc.xpath(".//graphml:node", namespaces=GRAPHML_NS)
node_dict = {node.get("id"):node for node in nodes}

# We are building a list of dictionaries with 3 keys (s, p, o) structure
triples = []
for edge in edges:
    try:
        p = edge.find(".//y:EdgeLabel", namespaces=GRAPHML_NS).text
    except:
        print("Some edges appear to be unlabeld. Check the output for missing values under the 'Predicate' column")
    s_id = edge.get("source")
    t_id = edge.get("target")
    source = node_dict[s_id]
    target = node_dict[t_id]
    s_list = source.findall(".//y:NodeLabel", namespaces=GRAPHML_NS)
    for el in s_list:
        sub_content = el.text
        if sub_content.strip():
            s = sub_content
    o_list = target.findall(".//y:NodeLabel", namespaces=GRAPHML_NS)
    for el in o_list:
        obj_content = el.text
        if obj_content.strip():
            o = obj_content
    triples.append({
        "subject":s,
        "Predicate":p,
        "Object":o
    })

df = pd.DataFrame(triples)
df.to_csv(path_or_buf="graph_data.csv", index=False)

# if __name__ == "__main__":
#     main()