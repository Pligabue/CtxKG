from pathlib import Path
import argparse
import json

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text

from cli_args import SIZE, MATCH

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

def main():
    SENTENCE_DIR = Path('./sentences')
    RESULTS_DIR = Path('./results')

    KG_NODE_DIRS = [dir for dir in RESULTS_DIR.glob(MATCH) if dir.is_dir()]
    
    for dir in KG_NODE_DIRS:
        base_dir = dir / "base"
        filenames = [file.stem for file in base_dir.glob("*.json")]
        abstracts = [read_file(file) for file in SENTENCE_DIR.glob("*.txt") if file.stem in filenames]

        abstract_encodings = cls_model(tf.constant(abstracts))
        similarity_matrix = get_similarity_matrix(abstract_encodings)
        
        data = {
            "filenames": filenames,
            "similarity_matrix": similarity_matrix.numpy().tolist()
        }

        with open(dir / "doc_similarity.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    main()