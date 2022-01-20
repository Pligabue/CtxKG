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
parser.set_defaults(size="small")
args = parser.parse_args()

THRESHOLD = args.threshold
SIZE = args.size
RATIO = args.ratio

SEP_ID = 102

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

def get_similarity_matrix(embeddings):
    normalized_embeddings = tf.math.l2_normalize(embeddings, 1)
    return tf.linalg.matmul(normalized_embeddings, normalized_embeddings, transpose_b=True)

def main():
    pira_df = pd.read_excel("data/pira.xlsx")
    grouped_by_abstract = pira_df.groupby("abstract")
    abstracts = pd.Series([abstract for abstract, _ in grouped_by_abstract])

    abstract_encodings = cls_model(abstracts)
    similarity_matrix = get_similarity_matrix(abstract_encodings)
    above_threshold_indices = np.argwhere(similarity_matrix > THRESHOLD)

    nodes = [None for _ in range(abstracts)]
    for i in range(abstracts):
        indices = above_threshold_indices[above_threshold_indices[:, 0] == i][:, 1]

if __name__ == "__main__":
    main()