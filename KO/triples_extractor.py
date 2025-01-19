import lxml.etree as etree
import pandas as pd 

GRAPHML_NS = {'graphml': 'http://graphml.graphdrawing.org/xmlns',
              'y': 'http://www.yworks.com/xml/graphml'}

path = "KO/05-conceptual_model.graphml"
# Parse the document
doc = etree.parse(path)

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
        sub_content = s_el.text.strip()
        obj_content = o_el.text.strip()
        # checking if the elements are empty or whitespace strings
        s = sub_content if sub_content else None
        o = obj_content if obj_content else None
    triples.append({
        "Subject":s,
        "Predicate":p,
        "Object":o
    }) # appending the triple dict to the list

df = pd.DataFrame(triples)
df.to_csv(path_or_buf="KO/graph_data.csv", index=False) # dump of all triples

# in this next section, we'll extract the triples involving each of the items we chose to represent, producing a separate CSV file for each of them

# the starting point is to list the names we assigned to each of the nodes representing said items
# set items in the list contain FRBR level for a single item
items = [
    set([
        ":WORK1",
        ":EXPRESSION2",
        ":EXPRESSION1",
        ":MANIFESTATION1",
        ":ITEM3",         
    ]),
    set([
        ":WORK18",
        ":EXPRESSION18",
        ":MANIFESTATION18",
        ":ITEM18",
    ]),
    set([
        ":WORK2",
        ":EXPRESSION4",    
        ":MANIFESTATION3",
        ":ITEM2"
    ]),
    set([
        ":WORK38",
        ":EXPRESSION38",
        ":MANIFESTATION38",
        ":ITEM38"
    ]),
    set([
        ":WORK4",
        ":EXPRESSION3",
        ":EXPRESSION44",
        ":MANIFESTATION2",
        ":ITEM1"
    ]),
    ":MAP1",
    ":PRINT1",
    ":PAINTING11",
    ":SCULPTURE1",
    ":MONUMENT1"
]

counter = 0 # for file naming purposes
for item in items:
    if isinstance(item, set):
        item_df = df[(df["Subject"].isin(item)) | (df["Object"].isin(item))]
        mask = ~(item_df["Object"].isin(item))
        mask2 = ~(item_df["Subject"].isin(item))
    else:
        item_df = df[(df["Subject"].str.contains(item)) | (df["Object"].str.contains(item))]
        mask = ~(item_df["Object"].str.contains(item))
        mask2 = ~(item_df["Subject"].str.contains(item))
    raw_objs = item_df["Object"][mask]
    raw_objs2 = item_df["Subject"][mask2]
    raw_objs = pd.concat([raw_objs, raw_objs2])
    print(raw_objs)
    objs = raw_objs[raw_objs.str.startswith(":")]
    final_mask = (df["Subject"].isin(objs)) & (df["Object"].str.startswith('"'))
    obj_literals = df[final_mask]
    final_df = pd.concat([item_df, obj_literals])
    path = f"KO/items_CSVs/item{counter}.csv"
    final_df.to_csv(path, index=False)
    counter += 1

