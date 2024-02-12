from adapters import Adapter
from rdflib import Graph
import os
import urllib.request
import gzip


class IsotopologueAdapter(Adapter):

    ALLOWED_TYPES = ['is isotopologue of']
    ALLOWED_LABELS = ['is_isotopologue_of']

    def __init__(self, url, type, label):
        if type not in IsotopologueAdapter.ALLOWED_TYPES:
            raise ValueError('Invalid type. Allowed values: ' +
                             ', '.join(IsotopologueAdapter.ALLOWED_TYPES))
        if label not in IsotopologueAdapter.ALLOWED_LABELS:
            raise ValueError('Invalid label. Allowed values: ' +
                             ', '.join(IsotopologueAdapter.ALLOWED_LABELS))

        self.url = url # "https://ftp.ncbi.nlm.nih.gov/pubchem/RDF/compound/general/pc_compound2isotopologue.ttl.gz"
        self.dataset = label
        self.type = type
        self.label = label
        self.source = "PubChem"
        self.source_url = "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"


    def get_edges(self):
        # Download the file
        filename = self.url.split('/')[-1]
        filepath = os.path.join('./', filename)
        urllib.request.urlretrieve(self.url, filepath)

        # Extract the file
        with gzip.open(filepath, 'rb') as f_in:
            isotopologue_ttl = f_in.read().decode('utf-8')

            # Load the Turtle file into an RDF Graph
            g = Graph()
            g.parse(isotopologue_ttl, format="ttl")

            for sub, _, obj in g:
                # Extract the local name of the subject and object
                subject_id = sub.split('/')[-1]
                object_id = obj.split('/')[-1]
            
                _id = subject_id + '_' + object_id
                _source = subject_id
                _target = object_id
                _props = {
                    'source': self.source,
                    'source_url': self.source_url
                }
                print(_source, _target, self.label, _props)
                yield(_id, _source, _target, self.label, _props)

        # # Delete the extracted file
        # os.remove(filepath)

