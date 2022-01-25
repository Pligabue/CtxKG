import re
import numpy as np
import pandas as pd
from pathlib import Path
import argparse
import json
from datetime import datetime

from tqdm import tqdm

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--threshold", type=float, default=0.9)
parser.add_argument("--small", dest="size", action="store_const", const="small")
parser.add_argument("--medium", dest="size", action="store_const", const="medium")
parser.add_argument("--big", dest="size", action="store_const", const="big")
parser.add_argument("-r", "--ratio", type=float, default=0.75)
parser.add_argument("-m", "--match", type=str, default="kg_nodes_ratio_*_threshold_*_*")
parser.add_argument("-g", "--groups", type=int, default=3)
parser.set_defaults(size="small")
args = parser.parse_args()

THRESHOLD = args.threshold
SIZE = args.size
RATIO = args.ratio
MATCH = args.match
GROUPS = args.groups

tfhub_handle_preprocess = "https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3"
tfhub_handle_encoder = {
    "big": "https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4",
    "medium": "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-8_H-512_A-8/2",
    "small": "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/2"
}[SIZE]

text_input = tf.keras.layers.Input(shape=(), dtype=tf.string)
preprocessor = hub.KerasLayer(tfhub_handle_preprocess)
encoder_inputs = preprocessor(text_input)
encoder = hub.KerasLayer(tfhub_handle_encoder)
outputs = encoder(encoder_inputs)
cls_model = tf.keras.Model(text_input, outputs["pooled_output"])

def read_file(file):
    with open(file, "r", encoding="utf-8") as f:
        return f.read()

def get_similarity_matrix(embeddings):
    normalized_embeddings = tf.math.l2_normalize(embeddings, 1)
    return tf.linalg.matmul(normalized_embeddings, normalized_embeddings, transpose_b=True)

def get_similar_filenames(filename, limit, doc_similarities):
    filename_index = doc_similarities["filenames"].index(filename)
    similarity_list = doc_similarities["similarity_matrix"][filename_index]
    
    names_similarities = zip(doc_similarities["filenames"], similarity_list)
    filtered_names_similarities = [ns for ns in names_similarities if ns[0] != filename]
    sorted_names_similarities = sorted(filtered_names_similarities, key=lambda ns: ns[1], reverse=True)
    
    return [name for name, similarity in sorted_names_similarities[:limit]]

def main():
    CLEAN_DIRS = [dir / "clean" for dir in Path('./results').glob(MATCH) if (dir / "clean").is_dir()]
    
    with open("./results/doc_similarity.json", "r", encoding="utf-8") as f:
        doc_similarities = json.load(f)

    for dir in CLEAN_DIRS:
        filenames = [file.stem for file in dir.glob("*.json") if file.stem in doc_similarities["filenames"]]

        for filename in filenames:
            similar_filenames = get_similar_filenames(filename, GROUPS, doc_similarities)
            break


if __name__ == "__main__":
    main()