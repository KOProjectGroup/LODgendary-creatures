import lxml.etree as et
import lxml
from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, FOAF, XSD, DC, DCTERMS, OWL

# NAMESPACES

schema = Namespace("https://schema.org/")
cidoc = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
owl = Namespace("http://www.w3.org/2002/07/owl#")
viaf = Namespace("http://viaf.org/viaf/")

project_root = "https://w3id.org/LODgendaryCreatures/"
lodc = Namespace(project_root) # defining our own namespace for URIs

doc = et.parse("KR/monstrorum_historia.xml")
tei_namespace = {"tei":"http://www.tei-c.org/ns/1.0"}

graph = Graph()
property_map = {
    "title": cidoc + ":P102 has title",
    "author": DCTERMS.creator,
    "date": DCTERMS.issued,
    "publisher": schema + "title",
    "pubPlace": DCTERMS.coverage,
    "editor": schema + "publisher",
    "idno": schema + "productId" 
}

# getting the node documenting the source of the encoding
source_desc = doc.find(".//tei:sourceDesc/tei:bibl", namespaces=tei_namespace)
source_uri = URIRef(lodc + "source")
for el in source_desc:
    tag = el.tag.split("}")[1]
    p = property_map.get(tag)
    o = el.text
    graph.add(source_uri, p, o)

# getting all the people referenced in the doc



# getting all the places referenced in the doc