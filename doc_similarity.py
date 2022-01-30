from pathlib import Path
import argparse
import json

import tensorflow as tf

from build_kg_nodes import get_models, get_similarity_matrix
from cli_args import SIZE, MATCH

def read_file(file):
    with open(file, "r", encoding="utf-8") as f:
        return f.read()

def main():
    SENTENCE_DIR = Path('./sentences')
    RESULTS_DIR = Path('./results')

    KG_NODE_DIRS = [dir for dir in RESULTS_DIR.glob(MATCH) if dir.is_dir()]
    
    _, _, cls_model = get_models(size=SIZE)
    
    for dir in KG_NODE_DIRS:
        base_dir = dir / "base"
        filenames = [file.stem for file in base_dir.glob("*.json")]
        abstracts = [read_file(file) for file in SENTENCE_DIR.glob("*.txt") if file.stem in filenames]

        abstract_encodings = cls_model(tf.constant(abstracts))
        similarity_matrix = get_similarity_matrix(abstract_encodings)
        
        data = {
            "filenames": filenames,
            "similarity_matrix": similarity_matrix.numpy().tolist()
        }

        with open(dir / "doc_similarity.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()