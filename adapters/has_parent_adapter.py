import os
from uu import Error
from xml.sax.handler import EntityResolver
import rdflib
from rdflib import *
from tqdm import tqdm
from adapters import Adapter
from biocypher._logger import logger

import requests


class HasParentAdapter(Adapter):
    DRY_RUN = 10
    SOURCE = "pubchem"
    VERSION = "1.0"
    HAS_PARENT = rdflib.term.URIRef(
        "https://rdf.ncbi.nlm.nih.gov/pubchem/vocabulary.owl#has_parent"
    )
    COMPOUNDS = {}

    def __init__(self, filepath=None, label="has_parent", dry_run=False):
        self.label = label
        if not filepath:
            logger.error("Input file not specified")
            raise ValueError("Input file not specified")

        if not os.path.exists(filepath):
            logger.error(f"Input file {filepath} doesn't exist")
            raise FileNotFoundError(f"Input file {filepath} doesn't exist")

        # To convert the file path to format tolerable suitable for the owlready
        filepath = os.path.realpath(filepath)

        self.dry_run = dry_run
        HasParentAdapter.COMPOUNDS[label] = f"file://{filepath}"
        self.file_path = filepath
        self.graph = None

    def __get_graph(self):
        graph = Graph()
        graph.parse(self.file_path, format="ttl")
        return graph

    def get_edges(self):
        self.graph = self.__get_graph()
        subject_objects = list(self.graph.subject_objects())

        nodes_dict = {}

        for entry in subject_objects:
            (subject, object) = entry
            nodes_dict[subject] = object

        nodes = nodes_dict.keys()
        nodes = list(nodes)[: HasParentAdapter.DRY_RUN] if self.dry_run else nodes

        i = 0  # dry run is set to true just output the first nodes until DRY_RUN constant
        for node in tqdm(nodes, desc="Loading parents", unit="compound"):
            if i > HasParentAdapter.DRY_RUN and self.dry_run:
                break

            # avoiding blank nodes and other arbitrary node types
            if not isinstance(node, rdflib.term.URIRef):
                continue

            source_id = HasParentAdapter.to_key(node)
            target_id = HasParentAdapter.to_key(nodes_dict[node])

            if not (source_id and target_id):
                continue
            props = {
                "source": HasParentAdapter.SOURCE,
                "version": HasParentAdapter.VERSION,
                "source_url": HasParentAdapter.COMPOUNDS[self.label],
            }
            i += 1
            yield source_id, source_id, target_id, self.label, props

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
