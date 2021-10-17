from re import sub
import pandas as pd
from pathlib import Path
import argparse
import json
import re
from datetime import datetime

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

text_input = tf.keras.layers.Input(shape=(), dtype=tf.string)
preprocessor = hub.KerasLayer(tfhub_handle_preprocess)
encoder_inputs = preprocessor(text_input)
encoder = hub.KerasLayer(tfhub_handle_encoder)
outputs = encoder(encoder_inputs)
pooled_output = outputs["pooled_output"]
embedding_model = tf.keras.Model(text_input, pooled_output)

def get_similarity_matrix(embeddings):
    normalized_embeddings = tf.math.l2_normalize(embeddings, 1)
    return tf.linalg.matmul(normalized_embeddings, normalized_embeddings, transpose_b=True)


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
            df = base_df[base_df["confidence"] > 0.70]
            if df.empty:
                empty_files.append(file.name)
                continue

            subjects = df["subject"]
            objects = df["object"]
            entities = subjects.append(objects, ignore_index=True)
            size = len(subjects)

            model_output = embedding_model(tf.constant(entities))

            entities_matrix = get_similarity_matrix(model_output)

            nodes = []
            for i in range(size):
                subject_index = i
                object_index = i + size
                
                subject_results = entities_matrix[subject_index]
                subject_link_indexes = [j for j, v in enumerate(subject_results) if v > THRESHOLD and j != subject_index and j != object_index]
                subject_links = list(set(entities.iloc[subject_link_indexes]))

                object_results = entities_matrix[object_index]
                object_link_indexes = [j for j, v in enumerate(object_results) if v > THRESHOLD and j != subject_index and j != object_index]
                object_links = list(set(entities.iloc[object_link_indexes]))

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
            failed_files.append(f"{datetime.now()}: {file.name} - {e}")

    with open("results/failed_files.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(failed_files))

    with open("results/empty_files.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(empty_files))

if __name__ == "__main__":
    main()