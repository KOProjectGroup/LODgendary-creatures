from rdflib import Graph, Namespace, URIRef, Literal, XSD
import pandas as pd
import re


# Custom uri for our project
project_root = "https://w3id.org/LODgendaryCreatures/"

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

lodc = Namespace(project_root) # defining our own Namespace

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
data = data.map(lambda x: x.replace(" ", "_") if "xsd" not in x else x)

for _, row in data.iterrows():

    subj_field = row["Subject"]
    prop_field = row["Predicate"]
    obj_field = row["Object"]

    print(subj_field, prop_field, obj_field)

    # Subject
    if subj_field.startswith(":"):
        subj_field = subj_field.strip(":")
        prefix = re.sub(r"\d+", "", subj_field)
        s = URIRef(lodc + prefix.lower() + "/" + subj_field)
    else:
        subj_components = subj_field.split(":")
        s = URIRef(abbreviations[subj_components[0]] + subj_components[1])

    # Predicate
    prop_components = prop_field.split(":")
    p = URIRef(abbreviations[prop_components[0]] + prop_components[1])

    # Object/Literal
    if "^^" in obj_field:
        lit_components = obj_field.split("^^")
        value = lit_components[0].strip('"')
        datatype = datatypes_table[lit_components[1]]
        o = Literal(value, datatype=datatype)
    elif obj_field.startswith(":"):
        obj_field = obj_field.strip(":")
        prefix = re.sub(r"\d+", "", obj_field)
        o = URIRef(lodc + prefix.lower() + "/" + obj_field)
    else:
        obj_components = obj_field.replace(" ", "_").split(":")
        o = URIRef(abbreviations[obj_components[0]] + obj_components[1])
    
    graph.add((s, p, o))

graph.serialize(destination="KR/items.ttl", format="turtle")