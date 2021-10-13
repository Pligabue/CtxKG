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
parser.add_argument("-t", "--threshold", type=float, default=0.9)
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
    normalized_embeddings = tf.math.l2_normalize(embeddings, 1)
    transposed_normalized_embeddings = tf.transpose(normalized_embeddings)
    return tf.linalg.matmul(normalized_embeddings, transposed_normalized_embeddings)


def main():

    TRIPLE_DIR = Path("./triples")
    KG_NODE_DIR = Path(f"./kg_nodes_{int(100 * THRESHOLD)}_{SIZE}")
    KG_NODE_DIR.mkdir(exist_ok=True)

    failed_files = []
    empty_files = []
    files = [file for file in TRIPLE_DIR.glob("*.txt") if not Path(KG_NODE_DIR / f"{file.stem}.json").is_file()]
    for file in tqdm(files):
        try:
            base_df = pd.read_csv(file, sep=";", names=["confidence", "subject", "relation", "object"])
            df = base_df[base_df["confidence"] > 0.9]
            if df.empty:
                empty_files.append(file.name)
                continue

            triples = df.apply(lambda row: " ".join(row[["subject", "relation", "object"]]).replace("�", ""), axis=1)
            subjects = df["subject"]
            objects = df["object"]
            size = len(triples)

            inputs = triples.append(subjects, ignore_index=True).append(objects, ignore_index=True)
            preprocessed_inputs = bert_preprocess_model(inputs)
            outputs = bert_model(preprocessed_inputs)["pooled_output"]

            triples_encodings = outputs[:size]
            subjects_encodings = outputs[size:size*2] + triples_encodings
            objects_encodings = outputs[size*2:] + triples_encodings

            subjects_matrix = get_similarity_matrix(subjects_encodings)
            objects_matrix = get_similarity_matrix(objects_encodings)

            if len(subjects_matrix) != len(objects_matrix):
                raise Exception("Matrices have different lengths")

            nodes = []
            for i, _ in enumerate(subjects_matrix):
                subject_results = subjects_matrix[i]
                subject_link_indexes = [j for j, v in enumerate(subject_results) if v > THRESHOLD and j != i]
                subject_links = list(set(subjects.iloc[subject_link_indexes]))

                object_results = objects_matrix[i]
                object_link_indexes = [j for j, v in enumerate(object_results) if v > THRESHOLD and j != i]
                object_links = list(set(objects.iloc[object_link_indexes]))

                nodes.append({
                    "subject": subjects.iloc[i],
                    "subject_links": subject_links,
                    "relation": df.iloc[i]["relation"],
                    "object": objects.iloc[i],
                    "object_links": object_links
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