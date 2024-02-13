# PubChem to MeTTa

This repo uses a [BioCypher](https://biocypher.org/) driven approach to represent PubChem RDF data and map them to MeTTa files. 

You can follow these steps to map these [compound PubChem RDF files](https://ftp.ncbi.nlm.nih.gov/pubchem/RDF/compound/general/) into MeTTa.

1. **Install [poetry](https://python-poetry.org/docs/) using `pipx`:**
```bash
pipx install poetry
```
2. **Install all required dependencies:**
```bash
poetry install
```
3. **Activate poetry virtual environment:**
```bash
poetry shell
```
4. **Run `main()` to generate the MeTTa files for PubChem:**
```bash
python create_knowledge_graph.py
```


- Once the MeTTa files are generated, the **nodes** and **edges** for the adapters will be stored in the `metta_out` folder, within their corresponding sub-folders.
- You can find some sample PubChem RDF data to be mapped to MeTTa stored in the `samples` folder. 
- If you want to map more PubChem data to MeTTa, you can download the RDF(turtle) files and and add the file paths to their corresponding adapter configs in the `create_knowledge_graph.py` module.