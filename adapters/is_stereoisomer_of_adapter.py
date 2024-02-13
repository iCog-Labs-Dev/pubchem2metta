from adapters import Adapter
from rdflib import Graph
from tqdm import tqdm
import gzip, os
from biocypher._logger import logger

class StereoisomerAdapter(Adapter):

    DRY_RUN = 100

    def __init__(self, filepath, label='is_stereoisomer_of', dry_run=False):
        if not filepath:
            logger.error("Input file not specified")
            raise ValueError("Input file not specified")
        if not os.path.exists(filepath):
            logger.error(f"Input file {filepath} doesn't exist")
            raise FileNotFoundError(f"Input file {filepath} doesn't exist")

        self.filepath = filepath
        self.dataset = label
        self.label = label
        self.dry_run = dry_run
        self.source = "PubChem"
        self.source_url = "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"
        self.version = "1.0"

    def get_edges(self):
        g = Graph()

        # Extract the file
        with gzip.open(self.filepath, 'rb') as f:
            g.parse(f, format='turtle')

        i = 0
        for subj, pred, obj in tqdm(g, desc="Running adapter: is_stereoisomer_of", unit="compound"):
            if i > StereoisomerAdapter.DRY_RUN and self.dry_run:
                break

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

            i += 1
            yield(_id, _source, _target, self.label, _props)

