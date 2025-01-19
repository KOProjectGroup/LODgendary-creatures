from rdflib import Graph, Namespace, URIRef, Literal, XSD
import pandas as pd
import re
from pathlib import Path


# Custom uri for our project
PROJECT_ROOT = "https://w3id.org/LODgendaryCreatures/"
DESTINATION_PATH = "KR/items.ttl"
FILE_PATH = "KO/items_CSVs"
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
lodc = Namespace(PROJECT_ROOT) # defining our own Namespace

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

# datatype mapping for literals
datatypes_table = {
    "xsd:string":XSD.string,
    "xsd:date":XSD.date,
    "xsd:integer":XSD.integer
    }

# Graph we will populate with the data in the CSV
graph = Graph()

def csv_to_rdf(
        data: str,
        graph: Graph,
        abbr:dict,
        dtypes:dict):
    
    for key, value in abbr.items():
        graph.bind(key, value) # binding abbreviations to respective namespace within the graph

    # Processing data using Pandas
    data = pd.read_csv(data)
    data = data.map(lambda x: x.replace(" ", "_") if "xsd" not in x else x) # removing whitespaces which are not in a literal

    for _, row in data.iterrows():

        subj_field = row["Subject"]
        prop_field = row["Predicate"]
        obj_field = row["Object"]

        ### string processing for data cleaning and URI minting ### 

        # Subject
        if ":" not in subj_field: # condition to catch the main class (LegendaryCreatures) to create custom URI
            subj_field = subj_field.strip(":")
            s = URIRef(lodc + subj_field)
        elif subj_field.startswith(":"): # handling class instances
            subj_field = subj_field.strip(":")
            # prefix for all the individuals in input, automatically created based on their name
            # custom prefix for the instances of our main class (LegendaryCreatures)
            prefix = re.sub(r"\d+", "", subj_field).lower() if "CREATURE" not in subj_field else "LegendaryCreatures"
            s = URIRef(lodc + prefix + "/" + subj_field)
        else:
            subj_components = subj_field.split(":") # splitting prefixed entities (ex. schema:Place)
            s = URIRef(abbreviations[subj_components[0]] + subj_components[1])

        # Predicate
        prop_components = prop_field.split(":")
        p = URIRef(abbreviations[prop_components[0]] + prop_components[1])

        # Object/Literal
        if "^^" in obj_field: # handling literals separately
            lit_components = obj_field.split("^^")
            value = lit_components[0].strip('"')
            datatype = dtypes[lit_components[1]]
            o = Literal(value, datatype=datatype)
        elif ":" not in obj_field: # again, handling our main class
            obj_field = obj_field.strip(":")
            o = URIRef(lodc + "/" + obj_field)
        elif obj_field.startswith(":"):
            obj_field = obj_field.strip(":")
            prefix = re.sub(r"\d+", "", obj_field).lower() if "CREATURE" not in obj_field else "LegendaryCreatures"
            o = URIRef(lodc + prefix + "/" + obj_field)
        else:
            obj_components = obj_field.split(":")
            o = URIRef(abbreviations[obj_components[0]] + obj_components[1])
        
        graph.add((s, p, o)) # populating graph with each processed components of the dataframe
    return graph

if __name__ == "__main__":
    path = Path(FILE_PATH)
    if path .is_file(): # conversion of a single file
        graph = csv_to_rdf(
            data=FILE_PATH,
            graph=graph,
            abbr=abbreviations,
            dtypes=datatypes_table
        )
        graph.serialize(destination=DESTINATION_PATH, format="turtle")
    else:
        file_paths = [f for f in path.iterdir() if f.is_file()] # conversion of a directory of csv files
        print(file_paths)
        for file in file_paths:
            print(file)
            graph = csv_to_rdf(
                data=file,
                graph=graph,
                abbr=abbreviations,
                dtypes=datatypes_table
            )
        graph.serialize(destination=DESTINATION_PATH, format="turtle")