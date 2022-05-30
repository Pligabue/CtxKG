# Generating graphs

## Generate triples

Once the documents are in the `documents` directory, `python build_triples.py` must be run in order to convert each document into a triple using OpenIE. The triples are stores in the `triples` directory.

## Build knowledge graph

With the generated triples, the building of the knowledge graph is done by running `python build_kg_nodes.py`. This part uses a few CLI arguments:
- `-t`/`--threshold`: the minimum cosine for two entities to be considered synonyms.
- `-r`/`--ratio`: the ratio between the base entity encoding and the triple encoding for the generation of the final entity encoding.
- `-o`/`--overwrite`: if the graphs generated in a previous run should be redone.
- `--small`/`--medium`/`--big`: the size of the BERT encoder.

## Clean graphs

By running `python clean_nodes.py`, the previously generated graphs are cleaned, which means that synonyms are reduced into a single entity, the one among the synonyms that is the most recurring in the graph.

## Build bridges

To generate connections between different graphs, run `python build_kg_bridges`. This is by far the most time-consuming step, as all graphs are compared to each other. This part also uses CLI arguments:
- `-t`/`--threshold`: the minimum cosine for two entities to be considered synonyms.
- `-r`/`--ratio`: the ratio between the base entity encoding and the triple encoding for the generation of the final entity encoding.
- `-o`/`--overwrite`: if the bridges generated in a previous run should be redone.
- `--small`/`--medium`/`--big`: the size of the BERT encoder.
- `--clean`: if the clean graphs should be used. The clean graphs must have been generated through the previous step.

# Server

After installing the Python dependencies (`pip install -r requirements.txt`), run the Flask server by running `flask run`.