from pathlib import Path
import json

import tensorflow as tf

from build_kg_nodes import get_models, get_similarity_matrix
from cli_args import SIZE, MATCH

def read_file(file):
    with open(file, "r", encoding="utf-8") as f:
        return f.read()

def main():
    DOC_DIR = Path('./documents')
    RESULTS_DIR = Path('./results')

    KG_NODE_DIRS = [dir for dir in RESULTS_DIR.glob(MATCH) if dir.is_dir()]

    _, _, cls_model = get_models(size=SIZE)
    
    for dir in KG_NODE_DIRS:
        base_dir = dir / "base"
        filenames = [file.stem for file in base_dir.glob("*.json")]
        docs = [read_file(file) for file in DOC_DIR.glob("*.txt") if file.stem in filenames]

        doc_encodings = cls_model(tf.constant(docs))
        similarity_matrix = get_similarity_matrix(doc_encodings)
        
        data = {
            "filenames": filenames,
            "similarity_matrix": similarity_matrix.tolist()
        }

        with open(dir / "doc_similarity.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()