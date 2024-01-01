from owlready2 import *
from rdflib import Graph
import rdflib

# Create a new Graph
graph = Graph()

# Parse the Turtle file
graph.parse("file:///home/wendecoder/Downloads/pc_compound2component.ttl", format="turtle")

# for s, o in g.subject_objects():
#     print(s, o)

# onto = get_ontology("https://rdf.ncbi.nlm.nih.gov/pubchem/vocabulary.owl").load()
# onto.save()
# Save it as RDF/XML
graph.serialize(destination='file:///home/wendecoder/Downloads/pc_compound2component.owl', format='xml')

# onto2 = get_ontology("file:///home/wendecoder/Downloads/uberon.owl")

# # Load the RDF data from the rdflib graph into the ontology
# onto = get_ontology("file:///home/wendecoder/Downloads/pc_compound2component.owl").load()

# NAMESPACE = rdflib.term.URIRef(
#         'https://rdf.ncbi.nlm.nih.gov/pubchem/vocabulary.owl')
# # graph = default_world.as_rdflib_graph(onto)
# print(NAMESPACE)
# NAMESPACE = rdflib.term.URIRef(
#         'http://www.geneontology.org/formats/oboInOwl#hasOBONamespace')
# print(NAMESPACE)
# print(list(graph.predicates()))

# nodes_in_namespace = list(graph.subject_objects(
#             predicate=NAMESPACE))
# print(graph.all_nodes())
nodes_in_namespaces = graph.predicates()

# for p in nodes_in_namespaces:
#     print(p)# print(nodes_in_namespace)
# print(len(list(nodes_in_namespaces)))
print(list(nodes_in_namespaces))


# Print the individuals in the ontology
# for individual in onto.individuals():
#     print(individual)

# print(list(onto.classes()))
