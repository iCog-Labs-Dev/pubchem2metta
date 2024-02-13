from adapters.compound_adapter import CompoundAdapter
import rdflib
from owlready2 import *
from tqdm import tqdm
from adapters import Adapter
from biocypher._logger import logger
from adapters import *


class HasComponentEdge(CompoundAdapter):

    def __init__(self, filepath=None, label="has_component", dry_run=False):
        super().__init__(filepath=filepath, label=label, dry_run=False)
        self.type = "edge"
        self.compound_adapter_instance = CompoundAdapter(filepath=filepath, label=label, dry_run=dry_run)
        print(super().ONTOLOGIES)

    TYPE = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')

    HAS_COMPONENT = rdflib.term.URIRef("http://semanticscience.org/resource/CHEMINF_000480")

    PREDICATE = [HAS_COMPONENT]

    def get_edges(self):
        print(self.compound_adapter_instance.file_path)
        ontology = self.compound_adapter_instance.label
        self.graph = self.compound_adapter_instance._get_graph(ontology=ontology)
        # self.cache_edge_properties()
        for predicate in self.PREDICATE:
            edges = list(self.graph.subject_objects(predicate=predicate, unique=True))
            # print(edges)
            i = 0  # dry run is set to true just output the first 100 relationships
            for edge in tqdm(edges, desc="Loading compounds", unit="compound"):
                if i > 100 and self.dry_run:
                    break
                from_node, to_node = edge

                if self.is_blank(from_node):
                    continue

                # if self.is_blank(to_node) and self.is_a_restriction_block(to_node):
                #     restriction_predicate, restriction_node = self.read_restriction_block(to_node)
                #     if restriction_predicate is None or restriction_node is None:
                #         continue

                #     predicate = restriction_predicate
                #     to_node = restriction_node

                if self.type == 'edge':
                    from_node_key = self.compound_adapter_instance.to_key(from_node)
                    predicate_key = self.compound_adapter_instance.to_key(predicate)
                    to_node_key = self.compound_adapter_instance.to_key(to_node)

                    # predicate_name = self.predicate_name(predicate)
                    # if predicate_name == 'dbxref':
                    #     continue  # TODO should we skip dbxref edges?
                    key = '{}_{}_{}'.format(
                        from_node_key,
                        predicate_key,
                        to_node_key
                    )
                    props = {
                        'rel_type': self.predicate_name(predicate),
                        'source': 'PUBCHEM',
                        'source_url': self.compound_adapter_instance.file_path
                    }

                    yield key, from_node_key, to_node_key, self.label, props
                    i += 1

    # def cache_edge_properties(self):
    #     self.cache['node_types'] = self.cache_predicate(HasComponentEdge.TYPE)
    #     self.cache['on_property'] = self.cache_predicate(HasComponentEdge.ON_PROPERTY)
    #     self.cache['some_values_from'] = self.cache_predicate(HasComponentEdge.SOME_VALUES_FROM)
    #     self.cache['all_values_from'] = self.cache_predicate(HasComponentEdge.ALL_VALUES_FROM)

    def predicate_name(self, predicate):
        predicate = str(predicate)
        if predicate == str(HasComponentEdge.HAS_COMPONENT):
            return 'has_component'
        # elif predicate == str(HasComponentEdge.PART_OF):
        #     return 'part_of'
        # elif predicate == str(HasComponentEdge):
        #     return 'subclass'
        # elif predicate == str(HasComponentEdge):
        #     return 'dbxref'
        return ''
    
    def is_blank(self, node):
        # a BNode according to rdflib is a general node (as a 'catch all' node) that doesn't have any type such as Class, Literal, etc.
        BLANK_NODE = rdflib.term.BNode

        return isinstance(node, BLANK_NODE)