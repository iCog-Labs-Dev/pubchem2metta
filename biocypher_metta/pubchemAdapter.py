import os
import json
import rdflib
from owlready2 import *
from biocypher_metta.Adapter import Adapter
import requests
from bs4 import BeautifulSoup

class OntologyAdapter():
    SKIP_BIOCYPHER = True
    OUTPUT_PATH = './parsed-data'
    file_path = 'file:///home/wendecoder/Downloads/pc_compound2descriptor.owl'
    ONTOLOGIES = {
        
        'pcco': file_path,
    }

    HAS_ATTRIBUTE = rdflib.term.URIRef("http://semanticscience.org/resource/SIO_000008")
    HAS_PARENT = rdflib.term.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/vocabulary#has_parent")
    HAS_COMPONENT = rdflib.term.URIRef("http://semanticscience.org/resource/CHEMINF_000480")
    HAS_STEREOISOMER = rdflib.term.URIRef("http://semanticscience.org/resource/CHEMINF_000461")
    HAS_ISOTOPOLOGUE = rdflib.term.URIRef("http://semanticscience.org/resource/CHEMINF_000455")
    HAS_UNCHARGED_COUNTERPART = rdflib.term.URIRef("http://semanticscience.org/resource/CHEMINF_000477")
    HAS_SAME_CONNECTIVITY_WITH = rdflib.term.URIRef("http://semanticscience.org/resource/CHEMINF_000462")
    TYPE = rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    HAS_2D_SIMILAR_COMPOUND = rdflib.term.URIRef("http://semanticscience.org/resource/CHEMINF_000482")
    HAS_3D_SIMILAR_COMPOUND = rdflib.term.URIRef("http://semanticscience.org/resource/CHEMINF_000483")
    LABEL = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label')
    RESTRICTION = rdflib.term.URIRef(
        'http://www.w3.org/2002/07/owl#Restriction')
    DESCRIPTION = rdflib.term.URIRef("http://purl.org/dc/terms/description")
    ON_PROPERTY = rdflib.term.URIRef(
        'http://www.w3.org/2002/07/owl#onProperty')
    SOME_VALUES_FROM = rdflib.term.URIRef(
        'http://www.w3.org/2002/07/owl#someValuesFrom')
    ALL_VALUES_FROM = rdflib.term.URIRef(
        'http://www.w3.org/2002/07/owl#allValuesFrom')
    SUBCLASS = rdflib.term.URIRef(
        'http://www.w3.org/2000/01/rdf-schema#subClassOf')
    
    PREDICATES = [SUBCLASS, HAS_PARENT, HAS_ISOTOPOLOGUE, HAS_STEREOISOMER]
    RESTRICTION_PREDICATES = [HAS_COMPONENT, HAS_PARENT]

    def __init__(self, type='node', dry_run=False):
        self.type = type
        self.dry_run = False
        if type == 'node':
            self.label = 'ontology_term COMPOUND'
        elif type == 'edge':
            self.label = 'ontology_relationship'
        else:
            raise ValueError('Invalid type. Allowed values: node, edge')
        
    def getValue(self, id):
        print(id)
        url = url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{id}/JSON"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data
                
                
            else:
                print(f"Error: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")

        
        
    def get_graph(self, ontology):

        onto = get_ontology(OntologyAdapter.ONTOLOGIES[ontology]).load()
        self.graph = default_world.as_rdflib_graph()
        # self.graph = onto.as_rdflib_graph()
        self.clear_cache()
        return self.graph

    def get_nodes(self):

        for ontology in OntologyAdapter.ONTOLOGIES.keys():
            self.graph = self.get_graph(ontology)
            # print(list(self.graph.all_nodes()))
            self.cache_node_properties()
            # nodes_in_go_namespaces = self.find_go_nodes(self.graph)
            # nodes = nodes_in_go_namespaces.keys()
            subObject = list(self.graph.subject_objects())
            nodes_dict = {}
            for n in subObject:
                node = n[0]
                nodes_dict[node] = n[1]
            nodes = nodes_dict.keys()
            # print(list(nodes))
            # nodes = list(self.graph.subject_objects())
            i = 0 # dry run is set to true just output the first 1000 nodes
            for node in nodes:
                if i > 100 and self.dry_run:
                    break
                # print(node)
                # avoiding blank nodes and other arbitrary node types
                if not isinstance(node, rdflib.term.URIRef):
                    continue
                if str(node) == 'http://anonymous' or str(node) == self.file_path:
                    continue
                # print(node)
                # term_id = str(node).split('/')[-1]
                print(node)
                term_id = OntologyAdapter.to_key(node)
                data = self.getValue(term_id[3:])
                print("term id", term_id)
                # attribute = str(','.join(self.get_all_property_values_from_node(node, 'attributes')))
                # attributesList = attribute.split(',')
                # print(attributesList)
                props = {
                    # 'uri': str(node),44444444444444
                    # 'attribute' : ' '.join(self.get_all_property_values_from_node(node, 'attributes')),
                    # 'Canonical_SMILES' : self.getValue(attributesList[0]),
                    # 'Compound_Identifier' : self.getValue(attributesList[1]),
                    # 'Covalent_Unit_Count' : self.getValue(attributesList[2]),
                    # 'Defined_Atom_Stereo_Count' : self.getValue(attributesList[3]),
                    # 'Defined_Bond_Stereo_Count' : self.getValue(attributesList[4]),
                    # 'Exact_Mass' : self.getValue(attributesList[5]),
                    # 'Hydrogen_Bond_Acceptor_Count' : self.getValue(attributesList[6]),
                    # 'Hydrogen_Bond_Donor_Count' : self.getValue(attributesList[7]),
                    # 'IUPAC_InChI' : self.getValue(attributesList[8]),
                    # 'Isomeric_SMILES' : self.getValue(attributesList[9]),
                    # 'Isotope_Atom_Count' : self.getValue(attributesList[10]),
                    # 'Molecular_Formula' : self.getValue(attributesList[11]),
                    # 'Molecular_Weight' : self.getValue(attributesList[12]),
                    # 'Mono_Isotopic_Weight' : self.getValue(attributesList[13]),
                    # 'synonyms': self.get_all_property_values_from_node(node, 'related_synonyms') +
                    # self.get_all_property_values_from_node(node, 'exact_synonyms'),
                    # 'subontology': nodes_in_go_namespaces.get(node, None),
                    'source': ontology.upper(),
                    'source_url': f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{term_id[3:]}/JSON",

                }
                if 'PC_Compounds' in data:
                    compound_info = data['PC_Compounds'][0]
                    excluded_properties = ['SubStructure_Keys_Fingerprint', 'Allowed_IUPAC_Name', 'CAS-like_Style_IUPAC_Name', 'Markup_IUPAC_Name', 'Systematic_IUPAC_Name', 'Traditional_IUPAC_Name', 'Canonicalized_Compound']
                    for property in compound_info.get('props', []):
                        prop_name = f"{property['urn']['name']}_{property['urn']['label']}" if 'urn' in property and 'name' in property['urn'] else property['urn']['label']
                        prop_name = prop_name.replace(' ', '_')
                        if prop_name in excluded_properties:
                            continue
                        if prop_name == 'MonoIsotopic_Weight':
                            prop_name = 'Mono_Isotopic_Weight'
                        if prop_name == 'Polar_Surface_Area_Topological':
                            prop_name = 'TPSA'
                        value_key = next((key for key in ['sval', 'ival', 'binary', 'fval'] if key in property['value']), None)
                        prop_value = property['value'][value_key]
                        props[prop_name] = prop_value
                    for key, count in compound_info.get('count', []).items():
                        if key == 'heavy_atom':
                            props['Non-hydrogen_Atom_Count'] = count
                        if key == 'atom_chiral_def':
                            props['Defined_Atom_Stereo_Count'] = count
                        if key == 'atom_chiral_undef':
                            props['Undefined_Atom_Stereo_Count'] = count
                        if key == 'bond_chiral_def':
                            props['Defined_Bond_Stereo_Count'] = count
                        if key == 'bond_chiral_undef':
                            props['Undefined_Bond_Stereo_Count'] = count
                        if key == 'covalent_unit':
                            props['Covalent_Unit_Count'] = count
                        if key == 'isotope_atom':
                            props['Isotope_Atom_Count'] = count
                        
                    props['Total_Formal_Charge'] = compound_info.get('charge', '')
                        # print(props)
                i += 1
                yield term_id, self.label, props

    def get_edges(self):
        for ontology in OntologyAdapter.ONTOLOGIES.keys():
            self.graph = self.get_graph(ontology)
            self.cache_edge_properties()
            for predicate in OntologyAdapter.PREDICATES:
                edges = list(self.graph.subject_objects(
                    predicate=predicate, unique=True))
                i = 0  # dry run is set to true just output the first 100 relationships
                for edge in edges:
                    if i > 100 and self.dry_run:
                        break
                    from_node, to_node = edge

                    if self.is_blank(from_node):
                        continue

                    if self.is_blank(to_node) and self.is_a_restriction_block(to_node):
                        restriction_predicate, restriction_node = self.read_restriction_block(
                            to_node)
                        if restriction_predicate is None or restriction_node is None:
                            continue

                        predicate = restriction_predicate
                        to_node = restriction_node

                    if self.type == 'edge':
                        from_node_key = OntologyAdapter.to_key(from_node)
                        predicate_key = OntologyAdapter.to_key(predicate)
                        to_node_key = OntologyAdapter.to_key(to_node)

                        if predicate == OntologyAdapter.DB_XREF:
                            if to_node.__class__ == rdflib.term.Literal:
                                if str(to_node) == str(from_node):
                                    print('Skipping self xref for: ' + from_node_key)
                                    continue

                                # only accepting IDs in the form <ontology>:<ontology_id>
                                if len(str(to_node).split(':')) != 2:
                                    print(
                                        'Unsupported format for xref: ' + str(to_node))
                                    continue

                                to_node_key = str(to_node).replace(':', '_')

                                if from_node_key == to_node_key:
                                    print('Skipping self xref for: ' + from_node_key)
                                    continue
                            else:
                                print('Ignoring non literal xref: {}'.format(str(to_node)))
                                continue

                        predicate_name = self.predicate_name(predicate)
                        if predicate_name == 'dbxref': continue #TODO should we skip dbxref edges?
                        key = '{}_{}_{}'.format(
                            from_node_key,
                            predicate_key,
                            to_node_key
                        )
                        props = {
                            'rel_type': self.predicate_name(predicate),
                            'source': ontology.upper(),
                            'source_url': OntologyAdapter.ONTOLOGIES[ontology],
                        }

                        yield key, from_node_key, to_node_key, self.label, props
                        i += 1

        
    def predicate_name(self, predicate):
        predicate = str(predicate)
        if predicate == str(OntologyAdapter.HAS_PARENT):
            return 'has_parent'
        elif predicate == str(OntologyAdapter.HAS_COMPONENT):
            return 'has_component'
        elif predicate == str(OntologyAdapter.SUBCLASS):
            return 'subclass'
        elif predicate == str(OntologyAdapter.HAS_STEREOISOMER):
            return 'has_stereoisomer'
        elif predicate == str(OntologyAdapter.HAS_ISOTOPOLOGUE):
            return 'has_isotopologue'
        elif predicate == str(OntologyAdapter.HAS_2D_SIMILAR_COMPOUND):
            return 'has_2d_similar_compound'
        elif predicate == str(OntologyAdapter.HAS_3D_SIMILAR_COMPOUND):
            return 'has_3d_similar_compound'
        return ''
    
    @classmethod
    def to_key(cls, node_uri):
        key = str(node_uri).split('/')[-1]
        key = key.replace('#', '.').replace('?', '_')
        key = key.replace('&', '.').replace('=', '_')
        key = key.replace('/', '_').replace('~', '.')
        key = key.replace('_', ':')
        key = key.replace(' ', '')

        if key.replace('.', '').isnumeric():
            key = '{}_{}'.format('number', key)

        return key
    
    def is_a_restriction_block(self, node):
        node_type = self.get_all_property_values_from_node(node, 'node_types')
        return node_type and node_type[0] == OntologyAdapter.RESTRICTION

    def read_restriction_block(self, node):
        restricted_property = self.get_all_property_values_from_node(
            node, 'on_property')

        # assuming a restriction block will always contain only one `owl:onProperty` triple
        if restricted_property and restricted_property[0] not in OntologyAdapter.RESTRICTION_PREDICATES:
            return None, None

        restriction_predicate = str(restricted_property[0])

        # returning the pair (owl:onProperty value, owl:someValuesFrom or owl:allValuesFrom value)
        # assuming a owl:Restriction block in a rdf:subClassOf will contain only one `owl:someValuesFrom` or `owl:allValuesFrom` triple
        some_values_from = self.get_all_property_values_from_node(
            node, 'some_values_from')
        if some_values_from:
            return (restriction_predicate, some_values_from[0])

        all_values_from = self.get_all_property_values_from_node(
            node, 'all_values_from')
        if all_values_from:
            return (restriction_predicate, all_values_from[0])

        return (None, None)
    
    def is_blank(self, node):
        # a BNode according to rdflib is a general node (as a 'catch all' node) that doesn't have any type such as Class, Literal, etc.
        BLANK_NODE = rdflib.term.BNode

        return isinstance(node, BLANK_NODE)
    # it's faster to load all subject/objects beforehand
    def clear_cache(self):
        self.cache = {}

    def cache_edge_properties(self):
        self.cache['node_types'] = self.cache_predicate(OntologyAdapter.TYPE)
        self.cache['on_property'] = self.cache_predicate(OntologyAdapter.ON_PROPERTY)
        self.cache['some_values_from'] = self.cache_predicate(
            OntologyAdapter.SOME_VALUES_FROM)
        self.cache['all_values_from'] = self.cache_predicate(
            OntologyAdapter.ALL_VALUES_FROM)

    def cache_node_properties(self):
        self.cache['term_names'] = self.cache_predicate(OntologyAdapter.LABEL)
        self.cache['descriptions'] = self.cache_predicate(OntologyAdapter.DESCRIPTION)
        self.cache['attributes'] = self.cache_predicate(
            OntologyAdapter.HAS_ATTRIBUTE)
        self.cache['has_parent'] = self.cache_predicate(
            OntologyAdapter.HAS_PARENT)
        self.cache['has_component'] = self.cache_predicate(OntologyAdapter.HAS_COMPONENT)
        self.cache['has_same_connectivity_with'] = self.cache_predicate(OntologyAdapter.HAS_SAME_CONNECTIVITY_WITH)

    def cache_predicate(self, predicate):
        return list(self.graph.subject_objects(predicate=predicate))

    def get_all_property_values_from_node(self, node, collection):
        values = []
        for subject_object in self.cache[collection]:
            subject, object = subject_object
            if subject == node:
                values.append(str(object))
        return values

