from adapters.compound_adapter import CompoundAdapter
import rdflib
from owlready2 import *
from tqdm import tqdm
from adapters import Adapter
from biocypher._logger import logger
from adapters import *


class HasSameConnectivityAsEdge(Adapter):

    TYPE = rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

    RESTRICTION = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#Restriction")

    ON_PROPERTY = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#onProperty")

    SOME_VALUES_FROM = rdflib.term.URIRef(
        "http://www.w3.org/2002/07/owl#someValuesFrom"
    )

    ALL_VALUES_FROM = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#allValuesFrom")

    HAS_SAME_CONNECTIVITY_AS = rdflib.term.URIRef(
        "http://semanticscience.org/resource/CHEMINF_000462"
    )

    def __init__(self, filepath=None, label="has_same_connectivity_as", dry_run=False):
        self.label = label
        self.file_path = None
        if not filepath:
            logger.error("Input file not specified")
            raise ValueError("Input file not specified")

        if not os.path.exists(filepath):
            logger.error(f"Input file {filepath} doesn't exist")
            raise FileNotFoundError(f"Input file {filepath} doesn't exist")

        # To convert the file path to format tollerable suitable for the owlready
        filepath = os.path.realpath(filepath)

        self.dry_run = dry_run
        self.file_path = filepath

    def get_edges(self):
        self.graph = self.__get_graph()
        self.cache_edge_properties()

        edges = list(
            self.graph.subject_objects(
                predicate=self.HAS_SAME_CONNECTIVITY_AS, unique=True
            )
        )
        i = 0  # dry run is set to true just output the first 100 relationships
        for edge in tqdm(edges, desc="Loading compounds", unit="compound"):
            if i > 100 and self.dry_run:
                break
            from_node, to_node = edge

            if self.is_blank(from_node):
                continue

            from_node_key = self.to_key(from_node)
            predicate_key = self.to_key(self.HAS_SAME_CONNECTIVITY_AS)
            to_node_key = self.to_key(to_node)

            key = "{}_{}_{}".format(from_node_key, predicate_key, to_node_key)
            props = {
                "rel_type": "has_same_connectivity_as",
                "source": "PUBCHEM",
                "source_url": self.file_path,
            }

            yield key, from_node_key, to_node_key, self.label, props
            i += 1

    def is_blank(self, node):
        # a BNode according to rdflib is a general node (as a 'catch all' node) that doesn't have any type such as Class, Literal, etc.
        BLANK_NODE = rdflib.term.BNode

        return isinstance(node, BLANK_NODE)

    def __get_graph(self):
        graph = Graph()
        graph.parse(self.file_path, format="ttl")
        return graph

    @classmethod
    def to_key(cls, node_uri):
        key = str(node_uri).split("/")[-1]
        key = key.replace("#", ".").replace("?", "_")
        key = key.replace("&", ".").replace("=", "_")
        key = key.replace("/", "_").replace("~", ".")
        key = key.replace("_", ":")
        key = key.replace(" ", "")

        if key.replace(".", "").isnumeric():
            key = "{}_{}".format("number", key)

        return key

    def cache_edge_properties(self):
        self.cache["node_types"] = self.cache_predicate(HasSameConnectivityAsEdge.TYPE)
        self.cache["on_property"] = self.cache_predicate(
            HasSameConnectivityAsEdge.ON_PROPERTY
        )
        self.cache["some_values_from"] = self.cache_predicate(
            HasSameConnectivityAsEdge.SOME_VALUES_FROM
        )
        self.cache["all_values_from"] = self.cache_predicate(
            HasSameConnectivityAsEdge.ALL_VALUES_FROM
        )

    def cache_predicate(self, predicate):
        return list(self.graph.subject_objects(predicate=predicate))

    def clear_cache(self):
        self.cache = {}
