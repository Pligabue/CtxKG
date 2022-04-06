import numpy as np
import tensorflow as tf
from tensorflow.keras import Model
from tensorflow_hub import KerasLayer
import tensorflow_text as text

from src.triple import Triple

class Encoder:
    SEP_ID = 102
    tfhub_preprocess_url = "https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3"
    tfhub_encoder_urls = {
        "big": "https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4",
        "medium": "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-8_H-512_A-8/2",
        "small": "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/2"
    }

    def __init__(self, size="small", ratio=0.9):
        self.ratio: float = ratio

        text_input = tf.keras.layers.Input(shape=(), dtype=tf.string)
        preprocessor = KerasLayer(self.tfhub_preprocess_url)
        encoder_inputs = preprocessor(text_input)
        encoder = KerasLayer(self.tfhub_encoder_urls[size])
        outputs = encoder(encoder_inputs)

        self.preprocessor: KerasLayer = preprocessor
        self.sequence_model: Model = Model(text_input, outputs["sequence_output"])
        self.cls_model: Model = Model(text_input, outputs["pooled_output"])

    def build_entity_encodings(self, triples: list[Triple]):
        subject_inputs = tf.constant([triple.subject.text for triple in triples])
        object_inputs = tf.constant([triple.object.text for triple in triples])
        triples_inputs = tf.constant([triple.to_text() for triple in triples])

        triple_end_indexes = np.argmax(self.preprocessor(triples_inputs)["input_word_ids"] == self.SEP_ID, axis=1) 
        subject_end_indexes = np.argmax(self.preprocessor(subject_inputs)["input_word_ids"] == self.SEP_ID, axis=1)
        object_start_indexes = triple_end_indexes - (np.argmax(self.preprocessor(object_inputs)["input_word_ids"] == self.SEP_ID, axis=1) - 1)

        triple_encodings = self.sequence_model(triples_inputs)

        for t_end, sub_end, obj_start, encoding, triple in zip(triple_end_indexes, subject_end_indexes, object_start_indexes, triple_encodings, triples):
            base_subject_encoding = tf.reduce_mean(encoding[1:sub_end], 0)
            base_object_encoding = tf.reduce_mean(encoding[obj_start:t_end], 0)
            cls_encodings = encoding[0]

            subject_encoding = tf.add(base_subject_encoding * self.ratio, cls_encodings * (1 - self.ratio))
            object_encoding = tf.add(base_object_encoding * self.ratio, cls_encodings * (1 - self.ratio))

            triple.subject.add_encoding(subject_encoding)
            triple.object.add_encoding(object_encoding)

        return self