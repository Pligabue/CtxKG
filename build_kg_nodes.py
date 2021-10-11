from re import sub
import pandas as pd
from pathlib import Path
import argparse
import json
import re

from tqdm import tqdm

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--threshold", type=float, default=-0.95)
parser.add_argument("--small", dest="size", action="store_const", const="small")
parser.add_argument("--medium", dest="size", action="store_const", const="medium")
args = parser.parse_args()

THRESHOLD = args.threshold
SIZE = args.size or "small"

tfhub_handle_preprocess = "https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3"

if SIZE == "medium":
    tfhub_handle_encoder = "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-8_H-512_A-8/2" # SMALL BERT
else:
    tfhub_handle_encoder = "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/2" # MEDIUM BERT

bert_preprocess_model = hub.KerasLayer(tfhub_handle_preprocess)
bert_model = hub.KerasLayer(tfhub_handle_encoder)


def get_similarity_matrix(embeddings):

    cosine_loss = tf.keras.losses.CosineSimilarity(axis=1)
    
    similarity_matrix = []
    for embedding_1 in embeddings:
        row = []
        for embedding_2 in embeddings:
            cossine_similarity = cosine_loss([embedding_1], [embedding_2]).numpy()
            row.append(cossine_similarity)

        similarity_matrix.append(row)

    return similarity_matrix


def main():

    TRIPLE_DIR = Path("./triples")
    KG_NODE_DIR = Path(f"./kg_nodes_{int(-100 * THRESHOLD)}_{SIZE}")
    KG_NODE_DIR.mkdir(exist_ok=True)

    failed_files = []
    empty_files = []
    for file in tqdm(list(TRIPLE_DIR.glob("*.txt"))):
        try:
            base_df = pd.read_csv(file, sep=";", names=["confidence", "subject", "relation", "object"])
            df = base_df[base_df["confidence"] > 0.9]
            if df.empty:
                empty_files.append(file.name)
                continue

            triples = df.apply(lambda row: " ".join(row[["subject", "relation", "object"]]).replace("�", ""), axis=1)
            triples_preprocessed = bert_preprocess_model(triples)
            triples_encodings = bert_model(triples_preprocessed)["pooled_output"]

            subjects = df["subject"]
            subjects_preprocessed = bert_preprocess_model(subjects)
            base_subjects_encodings = bert_model(subjects_preprocessed)["pooled_output"]
            subjects_encodings = base_subjects_encodings + triples_encodings
            subjects_matrix = get_similarity_matrix(subjects_encodings)

            objects = df["subject"]
            objects_preprocessed = bert_preprocess_model(objects)
            base_objects_encodings = bert_model(objects_preprocessed)["pooled_output"]
            objects_encodings = base_objects_encodings + triples_encodings
            objects_matrix = get_similarity_matrix(objects_encodings)

            if len(subjects_matrix) != len(objects_matrix):
                raise Exception("Matrices have different lengths")

            nodes = []
            for i, _ in enumerate(subjects_matrix):
                subject_results = subjects_matrix[i]
                subject_node_indexes = [j for j, v in enumerate(subject_results) if v < THRESHOLD]
                subject_node = list(set(df.iloc[subject_node_indexes]["subject"]))

                relation = df.iloc[i]["relation"]

                object_results = objects_matrix[i]
                object_node_indexes = [j for j, v in enumerate(object_results) if v < THRESHOLD]
                object_node = list(set(df.iloc[object_node_indexes]["object"]))

                try:
                    same_node_index = next(j for j, node in enumerate(nodes) if node["subject"] == subject_node and node["relation"] == relation)
                    nodes[same_node_index]["object"] = list(set(nodes[same_node_index]["object"] + object_node))
                except StopIteration:
                    nodes.append({
                        "subject": subject_node,
                        "relation": relation,
                        "object": object_node
                    })

            with open(KG_NODE_DIR / f"{file.stem}.json", "w", encoding="utf-8") as f:
                json_string = json.dumps(nodes, indent=2)
                json_string = re.sub('\n {6}|\n {4}(?=\])', " ", json_string)
                json_string = re.sub('\[ ', "[", json_string)
                json_string = re.sub(' \]', "]", json_string)
                f.write(json_string)

        except Exception as e:
            failed_files.append(f"{file.name} - {e}")

    with open("results/failed_files.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(failed_files))

    with open("results/empty_files.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(empty_files))

if __name__ == "__main__":
    main()