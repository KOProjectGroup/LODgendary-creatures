import lxml.etree as et
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS, FOAF, XSD, DC, DCTERMS, OWL

# NAMESPACES

schema = Namespace("https://schema.org/")
cidoc = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
lrmoo = Namespace("http://www.cidoc-crm.org/lrmoo/")

project_root = "https://w3id.org/LODgendaryCreatures/"
lodc = Namespace(project_root) # defining our own namespace for URIs

# parsing TEI doc and defininig useful namespaces
doc = et.parse("KR/monstrorum_historia.xml")
NAMESPACES = {"tei":"http://www.tei-c.org/ns/1.0",
              "xml":"{http://www.w3.org/XML/1998/namespace}"}


graph = Graph() # rdf graph to be populated

# dict to map some elements to certain properties
properties_map = {
    "title": URIRef(cidoc + "P102_has_title"),
    "author": DCTERMS.creator,
    "date": DCTERMS.issued,
    "publisher": URIRef(schema + "title"),
    "pubPlace": DCTERMS.coverage,
    "editor": URIRef(schema + "publisher"),
    "idno": DCTERMS.identifier,
    "persName": FOAF.name,
    "birth": URIRef(schema + "birthDate"),
    "death": URIRef(schema + "deathDate")
}

# getting the node documenting the source of the encoding
source_desc = doc.find(".//tei:sourceDesc/tei:bibl", namespaces=NAMESPACES)
source_uri = URIRef(lodc + "source")

entity_type = URIRef(lrmoo + "F1_Work") # typing the source
graph.add((source_uri, RDF.type, entity_type))

for el in source_desc: # iterating over the source description child elements, extracting triples according to map
    tag = el.tag.split("}")[1]
    p = properties_map.get(tag)
    o = Literal(el.text) # all the properties mapped to these elements have literal ranges (for our convenience)
    graph.add((source_uri, p, o))

# getting all the people referenced in the doc
list_person = doc.findall(".//tei:particDesc/tei:listPerson/tei:person", namespaces=NAMESPACES)
pers_id_uri_mapping = {} # dict storing URIs for each referenced person, with temporary XML:ID as key
counter = 0 # counter for URI minting
for pers in list_person:
    # assigning URI and linking it to existing resources
    person_instance = URIRef(lodc + "person" + f"/PERSON{counter}")
    p = OWL.sameAs
    o = URIRef(pers.get("sameAs"))
    graph.add((person_instance, p, o))
    graph.add((person_instance, RDF.type, URIRef(cidoc+"E21_Person"))) # typing

    # adding person to dict
    pers_id = pers.get(NAMESPACES["xml"] + "id")
    pers_id_uri_mapping[pers_id] = person_instance
    
    # parsing the elements nested in each person element
    for pers_el in pers:
        tag = pers_el.tag.split("}")[1] # getting the tag to discriminate behaviour

        if tag == "persName":
            p = FOAF.name
            o = URIRef(lodc + "name" + f"/NAME{counter}") # minting a name URI to allow multiple labels assignments (different languages)
            label = Literal(pers_el.text, lang=pers_el.get(NAMESPACES["xml"] + "lang")) # getting the language attribute
            graph.add((o, RDFS.label, label))
            name_type = URIRef(cidoc + "E41_Appellation") # typing
            graph.add((o, RDF.type, name_type))
        else:
            # handling life-span dates
            p = properties_map.get(tag)
            o = Literal(pers_el.get("when"), datatype=XSD.string)
        graph.add((person_instance, p, o))
    counter += 1


# getting all the places referenced in the doc
places = doc.findall(".//tei:placeName", namespaces=NAMESPACES)
counter = 0
for place in places:
    place_uri = URIRef(lodc + "place" + f"/PLACE{counter}")
    p = FOAF.name
    o = Literal(place.text)

    entity_type = URIRef(schema + "Place")

    id = place.get("ref") # attribute for auth control

    graph.add((place_uri, p, o))
    graph.add((place_uri, RDF.type, entity_type))
    graph.add((place_uri, OWL.sameAs, URIRef(id)))


# getting all the works referenced in the doc
refs = doc.findall(".//tei:p//tei:bibl", namespaces=NAMESPACES)
counter = 0
for ref in refs:
    if "ref" in ref[0].tag: # skipping internal references (notes)
        continue
    work_uri = URIRef(lodc + "work" + f"/WORK{counter}")

    auth_ref = ref.find(".//tei:persName", NAMESPACES) # getting name of the mentioned author...

    if auth_ref is not None: # ...where present
        auth_id = auth_ref.get("ref").strip("#")
        auth = pers_id_uri_mapping.get(auth_id)
        graph.add((work_uri, DCTERMS.creator, auth))

    title_content = ref.find(".//tei:title", NAMESPACES).text # getting the referenced works's title
    title = Literal(title_content, datatype=XSD.string)
    graph.add((work_uri, DCTERMS.title, title))

    entity_type = URIRef(lrmoo + "F1_Work") # typing
    graph.add((work_uri, RDF.type, entity_type))

    counter += 1




graph.serialize(destination="KR/tei.ttl", format="turtle")