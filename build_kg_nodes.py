from re import sub, match
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
parser.add_argument("-o", "--overwrite", dest="overwrite", action="store_true")
parser.add_argument("-r", "--ratio", type=float, default=0.75)
parser.set_defaults(size="small", overwrite=False)
args = parser.parse_args()

THRESHOLD = args.threshold
SIZE = args.size
OVERWRITE = args.overwrite,
RATIO = args.ratio

COLON_ID = 1025
SEP_ID = 102

tfhub_handle_preprocess = "https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3"

if SIZE == "big":
    tfhub_handle_encoder = "https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4" # BIGGER BERT
elif SIZE == "medium":
    tfhub_handle_encoder = "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-8_H-512_A-8/2" # MEDIUM BERT
else:
    tfhub_handle_encoder = "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/2" # SMALL BERT

text_input = tf.keras.layers.Input(shape=(), dtype=tf.string)
preprocessor = hub.KerasLayer(tfhub_handle_preprocess)
encoder_inputs = preprocessor(text_input)
encoder = hub.KerasLayer(tfhub_handle_encoder)
outputs = encoder(encoder_inputs)
sequence_model = tf.keras.Model(text_input, outputs["sequence_output"])
cls_model = tf.keras.Model(text_input, outputs["pooled_output"])

def get_similarity_matrix(embeddings):
    normalized_embeddings = tf.math.l2_normalize(embeddings, 1)
    return tf.linalg.matmul(normalized_embeddings, normalized_embeddings, transpose_b=True)

def main():

    TRIPLE_DIR = Path("./triples")
    KG_NODE_DIR = Path(f"./kg_nodes_{int(100 * THRESHOLD)}_{SIZE}")
    KG_NODE_DIR.mkdir(exist_ok=True)

    failed_files = []
    empty_files = []
    files = [file for file in TRIPLE_DIR.glob("*.txt") if OVERWRITE or not Path(KG_NODE_DIR / f"{file.stem}.json").is_file()]
    sorted_files = sorted(files, key=lambda file: file.stat().st_size)
    for file in tqdm(sorted_files):
        try:
            base_df = pd.read_csv(file, sep=";", names=["confidence", "subject", "relation", "object"])
            df = base_df[base_df["confidence"] > 0.70]
            if df.empty:
                empty_files.append(file.name)
                continue

            triples = df.apply(lambda row: "; ".join(row[["subject", "relation", "object"]]), axis=1)
            n_triples = len(triples)

            subjects = df["subject"]
            objects = df["object"]
            entities = subjects.append(objects, ignore_index=True)

            triples_input = tf.constant(triples)

            input_word_ids = preprocessor(triples_input)["input_word_ids"]

            colon_indexes = np.argwhere(input_word_ids == COLON_ID)
            colon_positions = [colon_indexes[colon_indexes[:, 0] == i][:, 1] for i in range(n_triples)]

            end_indexes = np.argwhere(input_word_ids == SEP_ID)
            end_positions = [end_indexes[end_indexes[:, 0] == i][-1, 1] for i in range(n_triples)]

            triple_outputs = sequence_model(triples_input)

            subject_encodings = []
            object_encodings = []
            for i, triple_output in enumerate(triple_outputs):
                first_colon_position = colon_positions[i][0]
                last_colon_position = colon_positions[i][-1]
                end_position = end_positions[i]

                cls_output = triple_output[0]
                subject_avg = tf.reduce_mean(triple_output[1:first_colon_position], 0)
                object_avg = tf.reduce_mean(triple_output[last_colon_position:end_position], 0)
                subject_encodings.append(tf.add(subject_avg * RATIO, cls_output * (1 - RATIO)))
                object_encodings.append(tf.add(object_avg * RATIO, cls_output  * (1 - RATIO)))

            entity_similarity_matrix = get_similarity_matrix(tf.concat([subject_encodings, object_encodings], 0))
            above_treshold_indices = np.argwhere(entity_similarity_matrix > THRESHOLD)

            nodes = [None for _ in range(n_triples)]
            for i in range(n_triples):
                subject_link_indeces = above_treshold_indices[above_treshold_indices[:, 0] == i][:, 1]
                object_link_indeces = above_treshold_indices[above_treshold_indices[:, 0] == i + n_triples][:, 1]

                nodes[i] = {
                    "subject": subjects.iloc[i],
                    "subject_links": list(set(entities.iloc[subject_link_indeces]) - {subjects.iloc[i]}),
                    "relation": df.iloc[i]["relation"],
                    "object": objects.iloc[i],
                    "object_links": list(set(entities.iloc[object_link_indeces]) - {objects.iloc[i]})
                }

            with open(KG_NODE_DIR / f"{file.stem}.json", "w", encoding="utf-8") as f:
                json.dump(nodes, f, indent=2)

        except Exception as e:
            failed_files.append(f"{datetime.now()}: {file.name} - {e}")

    with open("results/failed_files.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(failed_files))

    with open("results/empty_files.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(empty_files))

if __name__ == "__main__":
    main()