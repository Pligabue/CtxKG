import pandas as pd
from pathlib import Path

import os
import shutil

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
from official.nlp import optimization  # to create AdamW optimizer

import matplotlib.pyplot as plt

import tokenize

tfhub_handle_preprocess = "https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3"
tfhub_handle_encoder = "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/1"

bert_preprocess_model = hub.KerasLayer(tfhub_handle_preprocess)
bert_model = hub.KerasLayer(tfhub_handle_encoder)

def main():
    pass
    TRIPLE_DIR = Path("./triples")

    for file in TRIPLE_DIR.glob("*.txt"):
        with open(file) as f:
            df = pd.read_csv(file, sep=";", names=["confidence", "subject", "relation", "object"])
            sentences = df.apply(lambda row: " ".join(row[["subject", "relation", "object"]]), axis=1)
            text_preprocessed = bert_preprocess_model(sentences)
            bert_results = bert_model(text_preprocessed)["default"]
            
            print(bert_results)
        break

if __name__ == "__main__":
    main()