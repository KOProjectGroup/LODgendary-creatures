from rdflib import Graph, Namespace, URIRef, Literal, XSD
import pandas as pd
import re


# Custom uri for our project
project_uri = "https://w3id.org/LODgendaryCreatures/"

# Creating namespace objects for the standards employed in the KO phase
aat = Namespace("http://vocab.getty.edu/aat/")
fo = Namespace("https://semantics.id/ns/example/film/")
schema = Namespace("https://schema.org/")
dcterms = Namespace("https://www.dublincore.org/specifications/dublin-core/dcmi-terms/")
cidoc = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
rdfs = Namespace("https://www.w3.org/2000/01/rdf-schema#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
edm = Namespace("http://www.europeana.eu/schemas/edm/")
dbo = Namespace("http://dbpedia.org/ontology/")
owl = Namespace("http://www.w3.org/2002/07/owl#")
prov = Namespace("http://www.w3.org/ns/prov#")
lrmoo = Namespace("http://www.cidoc-crm.org/lrmoo/")
geo = Namespace("http://www.opengis.net/ont/geosparql#")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
wikidata = Namespace("http://www.wikidata.org/entity/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
viaf = Namespace("http://viaf.org/viaf/")
wkm = Namespace("https://commons.wikimedia.org/wiki/")

lodc = Namespace(project_uri) # defining our own Namespace

# Conversion dict, mapping abbreviations in the CSV to respective namespaces
abbreviations = {
    "aat":aat,
    "fo":fo,
    "schema":schema,
    "dcterms":dcterms,
    "cidoc":cidoc,
    "rdfs":rdfs,
    "rdf":rdf,
    "edm":edm,
    "dbo":dbo,
    "owl":owl,
    "prov":prov,
    "lrmoo":lrmoo,
    "geo":geo,
    "skos":skos,
    "wikidata":wikidata,
    "lodc":lodc,
    "foaf":foaf,
    "VIAF":viaf,
    "wkm":wkm
    }

datatypes_table = {
    "xsd:string":XSD.string,
    "xsd:date":XSD.date,
    "xsd:integer":XSD.integer
    }

# Graph we will populate with the data in the CSV
graph = Graph()
for key, value in abbreviations.items():
    graph.bind(key, value) # binding abbreviations to respective namespace within the graph

# Processing data using Pandas
data = pd.read_csv("KO/graph_data.csv")
data = data.map(lambda x: x.replace(" ", "_").replace("-", "_"))

for _, row in data.iterrows():

    s_data = row["Subject"]
    p_data = row["Predicate"]
    o_data = row["Object"]

    print(s_data, p_data, o_data)

    # Subject
    if s_data.startswith(":"):
        s_data = s_data.strip(":")
        prefix = re.sub(r"\d+", "", s_data)
        s = URIRef(lodc + prefix.lower() + "/" + s_data)
    else:
        s_components = s_data.split(":")
        s = URIRef(abbreviations[s_components[0]] + s_components[1])

    # Predicate
    p_components = p_data.split(":")
    p = URIRef(abbreviations[p_components[0]] + p_components[1])

    # Object/Literal
    if "^^" in o_data:
        lit_components = o_data.split("^^")
        value = lit_components[0].strip('"')
        datatype = datatypes_table[lit_components[1]]
        o = Literal(value, datatype=datatype)
    elif o_data.startswith(":"):
        o_data = s_data.strip(":")
        prefix = re.sub(r"\d+", "", o_data)
        o = URIRef(lodc + prefix.lower() + "/" + o_data)
    else:
        o_components = o_data.replace(" ", "_").split(":")
        o = URIRef(abbreviations[o_components[0]] + o_components[1])
    
    graph.add((s, p, o))

graph.serialize(destination="KR/items.ttl", format="turtle")