from adapters import Adapter
from rdflib import Graph
from tqdm import tqdm
import gzip, os
from biocypher._logger import logger


class IsotopologueAdapter(Adapter):

    ALLOWED_TYPES = ['is isotopologue of']
    ALLOWED_LABELS = ['is_isotopologue_of']

    def __init__(self, filepath, type, label):
        if type not in IsotopologueAdapter.ALLOWED_TYPES:
            logger.error(f"Invalid type. Allowed values: {str(IsotopologueAdapter.ALLOWED_TYPES)}")
            raise ValueError(f"Invalid type. Allowed values: {str(IsotopologueAdapter.ALLOWED_TYPES)}")
        if label not in IsotopologueAdapter.ALLOWED_LABELS:
            logger.error(f"Invalid label. Allowed values: {str(IsotopologueAdapter.ALLOWED_LABELS)}")
            raise ValueError(f"Invalid label. Allowed values: {str(IsotopologueAdapter.ALLOWED_LABELS)}")
        if not filepath:
            logger.error("Input file not specified")
            raise ValueError("Input file not specified")
        if not os.path.exists(filepath):
            logger.error(f"Input file {filepath} doesn't exist")
            raise FileNotFoundError(f"Input file {filepath} doesn't exist")

        self.filepath = filepath # "https://ftp.ncbi.nlm.nih.gov/pubchem/RDF/compound/general/pc_compound2isotopologue.ttl.gz"
        self.dataset = label
        self.type = type
        self.label = label
        self.source = "PubChem"
        self.source_url = "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"
        self.version = "1.0"

    def get_edges(self):
        # Download the file
        # filename = self.url.split('/')[-1]
        # filepath = os.path.join('./', filename)
        # urllib.request.urlretrieve(self.url, filepath)
        
        g = Graph()

        # Extract the file
        with gzip.open(self.filepath, 'rb') as f:
            g.parse(f, format='turtle')

        for subj, pred, obj in tqdm(g, desc="Running adapter: is_isotopologue_of", unit="compound"):
            subject_id = subj.split('/')[-1]
            object_id = obj.split('/')[-1]

            _id = subject_id + '_' + object_id
            _source = subject_id
            _target = object_id
            _props = {
                'source': self.source,
                'source_url': self.source_url,
                'version': self.version
            }
            yield(_id, _source, _target, self.label, _props)

