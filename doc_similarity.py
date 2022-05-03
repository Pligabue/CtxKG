from pathlib import Path
import json

import tensorflow as tf

from src.encoder import Encoder
from cli_args import SIZE, MATCH

def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def read_file(file):
    with open(file, "r", encoding="utf-8") as f:
        return f.read()

def main():
    RESULTS_DIR = Path('./results')
    KG_NODE_DIRS = [dir for dir in RESULTS_DIR.glob(MATCH) if dir.is_dir()]
    encoder = Encoder(size=SIZE)
    
    for dir in KG_NODE_DIRS:
        base_dir = dir / "base"
        doc_filenames = set([doc_file for file in base_dir.glob("*.json") for doc_file in read_json(file)["documents"]])
        doc_files = [Path(filename) for filename in doc_filenames]
        docs = [read_file(file) for file in doc_files]

        doc_encodings = encoder.cls_model(tf.constant(docs))
        normalized_encodings = tf.math.l2_normalize(doc_encodings, 1)
        similarity_matrix = tf.linalg.matmul(normalized_encodings, normalized_encodings, transpose_b=True).numpy()
        
        data = {
            "filenames": [str(file) for file in doc_files],
            "similarity_matrix": similarity_matrix.tolist()
        }

        with open(dir / "doc_similarity.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()