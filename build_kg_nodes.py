import pandas as pd
from pathlib import Path
import argparse

from tqdm import tqdm

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
from official.nlp import optimization  # to create AdamW optimizer

import matplotlib.pyplot as plt

tfhub_handle_preprocess = "https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3"
tfhub_handle_encoder = "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/1"

bert_preprocess_model = hub.KerasLayer(tfhub_handle_preprocess)
bert_model = hub.KerasLayer(tfhub_handle_encoder)

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--threshold", type=float, default=-0.95)
args = parser.parse_args()
THRESHOLD = args.threshold

def get_similarity_matrix(df, embeddings):

    cosine_loss = tf.keras.losses.CosineSimilarity(axis=1)
    
    similarity_matrix = []
    for embedding_1 in embeddings:
        row = []
        for embedding_2 in embeddings:
            cossine_similarity = cosine_loss([embedding_1], [embedding_2]).numpy()
            row.append(cossine_similarity)

        similarity_matrix.append(row)

    return similarity_matrix


def get_above_threshold_results(similarity_matrix):

    above_threshold_results = []
    for i, row in enumerate(similarity_matrix):
        indexes = []
        similarities = []
        for j, value in enumerate(row):
            if i == j:
                continue
            if value < THRESHOLD:
                indexes.append(j)
                similarities.append(value)
        
        above_threshold_results.append({
            "indexes": indexes,
            "similarities": similarities,
            "avg_similarity": sum(similarities)/len(similarities) if similarities else 0.0
        })

    return above_threshold_results

def group_triples(above_threshold_results):

    group_indexes = [None for _ in above_threshold_results]
    current_group_index = -1
    
    for i, above_threshold_result in enumerate(above_threshold_results):
        if group_indexes[i] is None:
            current_group_index += 1

            group_indexes[i] = current_group_index
            for similar_index in above_threshold_result["indexes"]:
                group_indexes[similar_index] = current_group_index
        else:
            group_index = group_indexes[i]
            for similar_index in above_threshold_result["indexes"]:
                group_indexes[similar_index] = group_index

    groups = []
    for group_index in set(group_indexes):
        group = []
        for i, _ in enumerate(above_threshold_results):
            if group_indexes[i] == group_index:
                group.append(i)
        groups.append(group)

    return groups   

def get_node_from_group(df, above_threshold_results, group):
    group_results = [{"index": i, "result": result} for i, result in enumerate(above_threshold_results) if i in group]
    group_results.sort(key=lambda res: res["result"]["avg_similarity"])
    
    most_similar_index = group_results[0]["index"]
    for result in group_results:
        subject = df.iloc[result["index"]]["subject"].lower()
        if subject not in ["i", "you", "he", "she", "it", "they"]:
            most_similar_index = result["index"]
            break

    return df.iloc[most_similar_index]

def main():

    TRIPLE_DIR = Path("./triples")
    KG_NODE_DIR = Path(f"./kg_nodes_{int(-100 * THRESHOLD)}")
    KG_NODE_DIR.mkdir(exist_ok=True)

    failed_files = []
    empty_files = []
    for file in tqdm(list(TRIPLE_DIR.glob("*.txt"))):
        try:
            with open(file, encoding="utf-8") as f:
                base_df = pd.read_csv(file, sep=";", names=["confidence", "subject", "relation", "object"])
                df = base_df[base_df["confidence"] > 0.9]
                if df.empty:
                    empty_files.append(file.name)
                    continue
                sentences = df.apply(lambda row: " ".join(row[["subject", "relation", "object"]]).replace("�", ""), axis=1)
                text_preprocessed = bert_preprocess_model(sentences)
                bert_results = bert_model(text_preprocessed)["default"]
                sim_matrix = get_similarity_matrix(df, bert_results)
                above_threshold_results = get_above_threshold_results(sim_matrix)
                groups = group_triples(above_threshold_results)
                
            with open(KG_NODE_DIR / file.name, "w", encoding="utf-8") as f:
                nodes = []
                for group in groups:
                    # node = get_node_from_group(df, above_threshold_results, group)
                    subjects = "|".join(set(df.iloc[group]["subject"]))
                    relations = "|".join(set(df.iloc[group]["relation"]))
                    objects = "|".join(set(df.iloc[group]["object"]))
                    node_string = f'{subjects};{relations};{objects}'
                    nodes.append(node_string)
                f.write("\n".join(nodes))
        except Exception as e:
            failed_files.append(f"{file.name} - {e}")

    with open("results/failed_files.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(failed_files))

    with open("results/empty_files.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(empty_files))

if __name__ == "__main__":
    main()