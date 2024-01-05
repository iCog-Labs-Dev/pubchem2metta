import rdflib
from owlready2 import *
from tqdm import tqdm
from adapters import Adapter
from biocypher._logger import logger

import requests


class CompoundAdapter(Adapter):
    OUTPUT_PATH = "./parsed-data"

    ONTOLOGIES = {
        # "pubchem": "file:///home/wendecoder/Downloads/pc_compound2descriptor.owl",
    }

    HAS_ATTRIBUTE = rdflib.term.URIRef("http://semanticscience.org/resource/SIO_000008")
    HAS_PARENT = rdflib.term.URIRef(
        "http://rdf.ncbi.nlm.nih.gov/pubchem/vocabulary#has_parent"
    )
    HAS_COMPONENT = rdflib.term.URIRef(
        "http://semanticscience.org/resource/CHEMINF_000480"
    )
    HAS_STEREOISOMER = rdflib.term.URIRef(
        "http://semanticscience.org/resource/CHEMINF_000461"
    )
    HAS_ISOTOPOLOGUE = rdflib.term.URIRef(
        "http://semanticscience.org/resource/CHEMINF_000455"
    )
    HAS_SAME_CONNECTIVITY_WITH = rdflib.term.URIRef(
        "http://semanticscience.org/resource/CHEMINF_000462"
    )
    TYPE = rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    LABEL = rdflib.term.URIRef("http://www.w3.org/2000/01/rdf-schema#label")
    RESTRICTION = rdflib.term.URIRef("http://www.w3.org/2002/07/owl#Restriction")
    DESCRIPTION = rdflib.term.URIRef("http://purl.org/dc/terms/description")
    SUBCLASS = rdflib.term.URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf")

    PREDICATES = [SUBCLASS, HAS_PARENT, HAS_ISOTOPOLOGUE, HAS_STEREOISOMER]

    def __init__(self, filepath=None, label="compound", dry_run=False):
        self.label = label
        if not filepath:
            logger.error("Input file not specified")
            raise ValueError("Input file not specified")

        if not os.path.exists(filepath):
            logger.error(f"Input file {filepath} doesn't exist")
            raise FileNotFoundError(f"Input file {filepath} doesn't exist")

        # To convert the file path to format tollerable suitable for the owlready
        filepath = os.path.realpath(filepath)

        self.dry_run = dry_run
        CompoundAdapter.ONTOLOGIES[label] = f"file://{filepath}"
        self.file_path = filepath

    def __getValue(self, id):
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{id}/JSON"
        # logger.info(f"Loading {id} from {url}")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                errorMessage = response.json()["Fault"]["Message"]
                # logger.error(f"{errorMessage} Status {response.status_code}")
        except requests.RequestException as e:
            # logger.error(f"Request failed: {e}")
            return None

    def __get_graph(self, ontology):
        onto = get_ontology(CompoundAdapter.ONTOLOGIES[ontology]).load()
        self.graph = default_world.as_rdflib_graph()
        self.clear_cache()
        return self.graph

    def get_nodes(self):
        for ontology in CompoundAdapter.ONTOLOGIES.keys():
            self.graph = self.__get_graph(ontology)
            self.cache_node_properties()
            subject_objects = list(self.graph.subject_objects())

            nodes_dict = {}

            for entry in subject_objects:
                (subject, object) = entry
                nodes_dict[subject] = object

            nodes = nodes_dict.keys()
            nodes = list(nodes)[:100] if self.dry_run else nodes

            i = 0  # dry run is set to true just output the first 100 nodes
            for node in tqdm(nodes, desc="Loading compounds", unit="compound"):
                if i > 100 and self.dry_run:
                    break

                # avoiding blank nodes and other arbitrary node types
                if not isinstance(node, rdflib.term.URIRef):
                    continue
                # if str(node) == "http://anonymous" or "@prefix":
                #     continue
                term_id = CompoundAdapter.to_key(node)
                data = self.__getValue(term_id)
                # logger.info(f"Node: {node} with term id {term_id}")

                props = {}
                if data is None:
                    continue

                if "PC_Compounds" in data:
                    compound_info = data["PC_Compounds"][0]
                    excluded_properties = [
                        "SubStructure_Keys_Fingerprint",
                        "Allowed_IUPAC_Name",
                        "CAS-like_Style_IUPAC_Name",
                        "Markup_IUPAC_Name",
                        "Systematic_IUPAC_Name",
                        "Traditional_IUPAC_Name",
                        "Canonicalized_Compound",
                    ]
                    for property in compound_info.get("props", []):
                        prop_name = (
                            f"{property['urn']['name']}_{property['urn']['label']}"
                            if "urn" in property and "name" in property["urn"]
                            else property["urn"]["label"]
                        )
                        prop_name = prop_name.replace(" ", "_")
                        if prop_name in excluded_properties:
                            continue
                        if prop_name == "MonoIsotopic_Weight":
                            prop_name = "Mono_Isotopic_Weight"
                        if prop_name == "Polar_Surface_Area_Topological":
                            prop_name = "TPSA"
                        value_key = next(
                            (
                                key
                                for key in ["sval", "ival", "binary", "fval"]
                                if key in property["value"]
                            ),
                            None,
                        )
                        prop_value = property["value"][value_key]
                        props[prop_name] = prop_value

                    for key, count in compound_info.get("count", []).items():
                        if key == "heavy_atom":
                            props["Non-hydrogen_Atom_Count"] = count
                        if key == "atom_chiral_def":
                            props["Defined_Atom_Stereo_Count"] = count
                        if key == "atom_chiral_undef":
                            props["Undefined_Atom_Stereo_Count"] = count
                        if key == "bond_chiral_def":
                            props["Defined_Bond_Stereo_Count"] = count
                        if key == "bond_chiral_undef":
                            props["Undefined_Bond_Stereo_Count"] = count
                        if key == "covalent_unit":
                            props["Covalent_Unit_Count"] = count
                        if key == "isotope_atom":
                            props["Isotope_Atom_Count"] = count

                    props["Total_Formal_Charge"] = compound_info.get("charge", "")
                i += 1
                yield term_id, self.label, props

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

    @classmethod
    def extract_id(cls, id):
        try:
            match = re.search(r"\d{2,}", id)
            if match:
                return match.group()
            else:
                return ""

        except Exception as e:
            logger.error(f"{e}")
            return ""

    # it's faster to load all subject/objects beforehand
    def clear_cache(self):
        self.cache = {}

    def cache_node_properties(self):
        self.cache["term_names"] = self.cache_predicate(CompoundAdapter.LABEL)
        self.cache["descriptions"] = self.cache_predicate(CompoundAdapter.DESCRIPTION)
        self.cache["attributes"] = self.cache_predicate(CompoundAdapter.HAS_ATTRIBUTE)
        self.cache["has_parent"] = self.cache_predicate(CompoundAdapter.HAS_PARENT)
        self.cache["has_component"] = self.cache_predicate(
            CompoundAdapter.HAS_COMPONENT
        )
        self.cache["has_same_connectivity_with"] = self.cache_predicate(
            CompoundAdapter.HAS_SAME_CONNECTIVITY_WITH
        )

    def cache_predicate(self, predicate):
        return list(self.graph.subject_objects(predicate=predicate))
