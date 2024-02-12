from uu import Error
from xml.sax.handler import EntityResolver
import rdflib
from owlready2 import *
from tqdm import tqdm
from adapters import Adapter
from biocypher._logger import logger

import requests


class DescriptorAdapter(Adapter):

    SOURCE = "pubchem"
    VERSION = "1.0"

    MOLAR_MASS_UNIT = rdflib.term.URIRef(
        "http://semanticscience.org/resource/SIO_000008"
    )
    SQUARE_ANGSTROM = rdflib.term.URIRef("http://purl.obolibrary.org/obo/UO_0000324")
    # Key value pair of descriptors and their corresponding properties
    DESCRIPTORS = {
        "Mono_Isotopic_Weight": {
            "unit": "molar_mass_unit",
            "source_url": MOLAR_MASS_UNIT,
        },
        "Molecular_Weight": {
            "unit": "molar_mass_unit",
            "source_url": MOLAR_MASS_UNIT,
        },
        "Exact_Mass": {
            "unit": "molar_mass_unit",
            "source_url": MOLAR_MASS_UNIT,
        },
        "TPSA": {
            "unit": "square_angstrom",
            "source_url": SQUARE_ANGSTROM,
        },
        "Standard_InChI": None,
        "Isomeric_SMILES": None,
        "XLogP3-AA_Log_P": None,
        "Canonical_SMILES": None,
        "Standard_InChIKey": None,
        "Molecular_Formula": None,
        "Isotope_Atom_Count": None,
        "Covalent_Unit_Count": None,
        "Total_Formal_Charge": None,
        "Compound_Complexity": None,
        "Total_Formal_Charge": None,
        "Preferred_IUPAC_Name": None,
        "Rotatable_Bond_Count": None,
        "Non-hydrogen_Atom_Count": None,
        "Defined_Atom_Stereo_Count": None,
        "Defined_Bond_Stereo_Count": None,
        "Hydrogen_Bond_Donor_Count": None,
        "Undefined_Atom_Stereo_Count": None,
        "Undefined_Bond_Stereo_Count": None,
        "Hydrogen_Bond_Acceptor_Count": None,
    }

    def __init__(
        self,
        filepath=None,
        label="descriptor",
    ):
        self.label = label
        if filepath:
            raise Error("File input not implemented")

        if not os.path.exists(filepath):
            logger.error(f"Input file {filepath} doesn't exist")
            raise FileNotFoundError(f"Input file {filepath} doesn't exist")

        # DescriptorAdapter.DESCRIPTORS[label] = f"file://{filepath}"
        # self.file_path = filepath

    def get_nodes(self):
        if DescriptorAdapter.RUN_ONCE:
            return

        for descriptor in DescriptorAdapter.DESCRIPTORS.keys():

            entries = DescriptorAdapter.DESCRIPTORS.get(descriptor)
            nodes_dict = {}

            for entry in entries:
                subject, object = entry
                nodes_dict[subject] = object

            nodes = nodes_dict.keys()
            nodes = list(nodes)[:100] if self.dry_run else nodes

            i = 0  # dry run is set to true just output the first 100 nodes
            for node in tqdm(nodes, desc="Loading descriptors", unit="descriptor"):
                if self.dry_run:
                    break

                # avoiding blank nodes and other arbitrary node types
                if not isinstance(node, rdflib.term.URIRef):
                    continue
                # if str(node) == "http://anonymous" or "@prefix":
                #     continue
                term_id = descriptor
                data = entries
                # logger.info(f"Node: {node} with term id {term_id}")
                props = {}
                if data is None:
                    continue

                if data.get("source_url"):
                    source_url = data.get("source_url")
                    props["source_url"] = source_url
                if data.get("unit"):
                    unit = data.get("unit")
                    props["unit"] = unit

                props["id"] = term_id
                props["source"] = DescriptorAdapter.SOURCE
                props["version"] = DescriptorAdapter.VERSION

                i += 1
                yield term_id, self.node_label, props
