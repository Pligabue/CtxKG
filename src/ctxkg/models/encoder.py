import numpy as np
import tensorflow as tf
from keras import Model
from tensorflow_hub import KerasLayer
from transformers import TFBertTokenizer, TFAutoModel
from triple_extractor_ptbr_pligabue.constants import BERT_MODEL_NAME

from ...constants import ENGLISH_PREFIX, PORTUGUESE_PREFIX
from .triple import Triple


class Encoder:
    SEP_ID = 102
    tfhub_preprocess_url = "https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3"
    tfhub_encoder_urls = {
        "big": "https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4",
        "medium": "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-8_H-512_A-8/2",
        "small": "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/2"
    }

    def __init__(self, size="small", language=ENGLISH_PREFIX, ratio=1.0):
        self.ratio: float = ratio

        if language == ENGLISH_PREFIX:
            id_list_key, preprocessor, text_input, seq_out, pooled_out = self._english_bert_models(size)
        elif language == PORTUGUESE_PREFIX:
            id_list_key, preprocessor, text_input, seq_out, pooled_out = self._portuguse_bert_models()
        else:
            raise Exception(f"No BERT model found for {language}.")

        self.id_list_key = id_list_key
        self.preprocessor: KerasLayer = preprocessor
        self.sequence_model: Model = Model(text_input, seq_out)
        self.cls_model: Model = Model(text_input, pooled_out)

    def build_entity_encodings(self, triples: list[Triple], batch_size=None):
        batch_size = batch_size or len(triples)
        for i in range(0, len(triples), batch_size):
            batch = triples[i:i+batch_size]
            subject_inputs = tf.constant([triple.subject.text for triple in batch])
            object_inputs = tf.constant([triple.object.text for triple in batch])
            triples_inputs = tf.constant([triple.to_text() for triple in batch])

            # type: ignore
            triple_end_indexes = np.argmax(self.preprocessor(triples_inputs)[self.id_list_key] == self.SEP_ID, axis=1)  # type: ignore  # noqa: E501
            subject_end_indexes = np.argmax(self.preprocessor(subject_inputs)[self.id_list_key] == self.SEP_ID, axis=1)  # type: ignore  # noqa: E501
            object_input_lengths = np.argmax(self.preprocessor(object_inputs)[self.id_list_key] == self.SEP_ID, axis=1) - 1  # type: ignore  # noqa: E501
            object_start_indexes = triple_end_indexes - object_input_lengths

            triple_encodings = self.sequence_model(triples_inputs)

            triple_data = zip(triple_end_indexes, subject_end_indexes, object_start_indexes, triple_encodings, batch)  # type: ignore  # noqa: E501
            for t_end, sub_end, obj_start, encoding, triple in triple_data:
                base_subject_encoding = tf.reduce_mean(encoding[1:sub_end], 0)
                base_object_encoding = tf.reduce_mean(encoding[obj_start:t_end], 0)
                cls_encodings = encoding[0]

                subject_encoding = tf.add(base_subject_encoding * self.ratio, cls_encodings * (1 - self.ratio))
                object_encoding = tf.add(base_object_encoding * self.ratio, cls_encodings * (1 - self.ratio))

                triple.subject.add_encoding(subject_encoding)
                triple.object.add_encoding(object_encoding)

        return self

    def _english_bert_models(self, size):
        text_input = tf.keras.layers.Input(shape=(), dtype=tf.string)
        preprocessor = KerasLayer(self.tfhub_preprocess_url)
        encoder_inputs = preprocessor(text_input)
        encoder = KerasLayer(self.tfhub_encoder_urls[size])
        outputs = encoder(encoder_inputs)

        return (
            "input_word_ids",
            preprocessor,
            text_input,
            outputs["sequence_output"],  # type: ignore
            outputs["pooled_output"],  # type: ignore
        )

    def _portuguse_bert_models(self):
        text_input = tf.keras.layers.Input(shape=(), dtype=tf.string)
        preprocessor = TFBertTokenizer.from_pretrained(BERT_MODEL_NAME)
        encoder_inputs = preprocessor(text_input)
        encoder = TFAutoModel.from_pretrained(BERT_MODEL_NAME).bert
        outputs = encoder(encoder_inputs)

        return (
            "input_ids",
            preprocessor,
            text_input,
            outputs.last_hidden_state,
            outputs.pooler_output,
        )
