import numpy as np
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

from tqdm import tqdm

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text

from cli_args import SIZE, RATIO, THRESHOLD, MATCH, OVERWRITE

SEP_ID = 102

def get_models(size=SIZE):
    tfhub_handle_preprocess = "https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3"
    tfhub_handle_encoder = {
        "big": "https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4",
        "medium": "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-8_H-512_A-8/2",
        "small": "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/2"
    }[size]

    text_input = tf.keras.layers.Input(shape=(), dtype=tf.string)
    preprocessor = hub.KerasLayer(tfhub_handle_preprocess)
    encoder_inputs = preprocessor(text_input)
    encoder = hub.KerasLayer(tfhub_handle_encoder)
    outputs = encoder(encoder_inputs)
    sequence_model = tf.keras.Model(text_input, outputs["sequence_output"])
    cls_model = tf.keras.Model(text_input, outputs["pooled_output"])

    return preprocessor, sequence_model, cls_model

def get_entity_encodings(models, subjects, relations, objects, ratio=RATIO):
    preprocessor, sequence_model, cls_model = models
    triples = [f"{subject} {relation} {object}" for subject, relation, object in zip(subjects, relations, objects)]

    subject_inputs = tf.constant(subjects)
    object_inputs = tf.constant(objects)
    triples_inputs = tf.constant(triples)

    triple_end_indexes = np.argmax(preprocessor(triples_inputs)["input_word_ids"] == SEP_ID, axis=1) 
    subject_end_indexes = np.argmax(preprocessor(subject_inputs)["input_word_ids"] == SEP_ID, axis=1)
    object_start_indexes = triple_end_indexes - (np.argmax(preprocessor(object_inputs)["input_word_ids"] == SEP_ID, axis=1) - 1)

    triple_encodings = sequence_model(triples_inputs)

    subject_encodings = []
    object_encodings = []
    for t_end, sub_end, obj_start, encoding in zip(triple_end_indexes, subject_end_indexes, object_start_indexes, triple_encodings):
        base_subject_encoding = tf.reduce_mean(encoding[1:sub_end], 0)
        base_object_encoding = tf.reduce_mean(encoding[obj_start:t_end], 0)
        cls_encodings = encoding[0]

        subject_encoding = tf.add(base_subject_encoding * ratio, cls_encodings * (1 - ratio))
        object_encoding = tf.add(base_object_encoding * ratio, cls_encodings * (1 - ratio))

        subject_encodings.append(subject_encoding)
        object_encodings.append(object_encoding)

    return subject_encodings, object_encodings

def get_similarity_matrix(embeddings):
    normalized_embeddings = tf.math.l2_normalize(embeddings, 1)
    return tf.linalg.matmul(normalized_embeddings, normalized_embeddings, transpose_b=True)

def build_nodes(subjects, relations, objects, subject_encodings, object_encodings, threshold=THRESHOLD):
    entity_encodings = tf.concat([subject_encodings, object_encodings], 0)
    entity_similarity_matrix = get_similarity_matrix(entity_encodings)
    entity_link_mask_matrix = entity_similarity_matrix >= threshold

    entities = np.array(list(subjects) + list(objects))
    objects_base_index = len(subjects)

    nodes = []
    for i, (subject, relation, object) in enumerate(zip(subjects, relations, objects)):
        subject_link_mask = entity_link_mask_matrix[i]
        object_link_mask = entity_link_mask_matrix[objects_base_index + i]

        nodes.append({
            "subject": subject,
            "subject_links": list(set(entities[subject_link_mask]) - {subject}),
            "relation": relation,
            "object": object,
            "object_links": list(set(entities[object_link_mask]) - {object})
        })

    return nodes

def build_graph(models, subjects, relations, objects, ratio=RATIO, threshold=THRESHOLD):
    subject_encodings, object_encodings = get_entity_encodings(models, subjects, relations, objects, ratio=ratio)
    graph = build_nodes(subjects, relations, objects, subject_encodings, object_encodings, threshold=threshold)

    return graph

def main():
    TRIPLE_DIR = Path("./triples")
    KG_NODE_DIR = Path(f"./results/kg_nodes_ratio_{int(100 * RATIO)}_threshold_{int(100 * THRESHOLD)}_{SIZE}")
    KG_NODE_DIR.mkdir(exist_ok=True)
    BASE_DIR = KG_NODE_DIR / "base"
    BASE_DIR.mkdir(exist_ok=True)
    ERRORS_DIR = BASE_DIR / "errors"
    ERRORS_DIR.mkdir(exist_ok=True)

    models = get_models()

    failed_files = []
    empty_files = []
    files = [file for file in TRIPLE_DIR.glob(MATCH) if OVERWRITE or not Path(BASE_DIR / f"{file.stem}.json").is_file()]
    sorted_files = sorted(files, key=lambda file: file.stat().st_size)
    for file in tqdm(sorted_files):
        try:
            base_df = pd.read_csv(file, sep=";", names=["confidence", "subject", "relation", "object"])
            df = base_df[base_df["confidence"] > 0.70]
            if df.empty:
                empty_files.append(file.name)
                continue

            subjects = df["subject"]
            objects = df["object"]
            relations = df["relation"]

            graph = build_graph(models, subjects, relations, objects)

            with open(BASE_DIR / f"{file.stem}.json", "w", encoding="utf-8") as f:
                json.dump(graph, f, indent=2)
        except KeyboardInterrupt:
            break
        except Exception as e:
            failed_files.append(f"{datetime.now()}: {file.name} - {e}")

    with open(ERRORS_DIR / "failed_files.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(failed_files))

    with open(ERRORS_DIR / "empty_files.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(empty_files))

if __name__ == "__main__":
    main()