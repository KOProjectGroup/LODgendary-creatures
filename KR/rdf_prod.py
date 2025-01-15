from rdflib import Graph, Namespace, URIRef, Literal, XSD
import pandas as pd


# Path to our project's repo
path = "https://w3id.org/LODgendaryCreatures/"

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

lodc = Namespace(path) # defining our own Namespace

# Conversion dict mapping abbreviations in the CSV to the respective namespace
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
    "viaf": viaf
    }

xsd_table = {
    "xsd:string":XSD.string,
    "xsd:date":XSD.date,
    "xsd:integer":XSD.integer,
    "xsd:float":XSD.float
    }

# Graph we will populate with the data in the CSV
graph = Graph()
for key, value in abbreviations.items():
    graph.bind(key, value) # binding abbreviations to respective namespace within the graph

# Function populating the graph with the CSV data
def triple_to_RDFgraph(s:pd.Series, ) -> None:
    triple = []
    # Subject
    for item in s.items():
        if item.startswith(":"):
            triple.append(URIRef(lodc + item))
        if "^^" in item:
            lit_components = item.split("^^")
            value = lit_components[0]
            datatype = xsd_table[lit_components[1]]
            triple.append(Literal(value, datatype=datatype))
        else:
            components = item.split(":")
            uri = URIRef(abbreviations[components[0]] + components[1])
            triple.append(uri)
    graph.add(tuple(triple))



# Processing data using Pandas
data = pd.read_csv("graph_data.csv")
for _, row in data.iterrows():
    triple = []
    for _, item in row.items():
        item = item.replace(" ", "_")
        if item == "Legendary_Creatures" or item == "predicate":
            triple.append(Literal(" "))
        elif item.startswith(":"):
            triple.append(URIRef(lodc + item))
        elif "^^" in item:
            lit_components = item.split("^^")
            value = lit_components[0]
            datatype = xsd_table[lit_components[1]]
            triple.append(Literal(value, datatype=datatype))
        else:
            components = item.split(":")
            uri = URIRef(abbreviations[components[0]] + components[1])
            triple.append(uri)
    graph.add(tuple(triple))

graph.serialize(destination="items.ttl", format="turtle")
    