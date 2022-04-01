from typing import Dict, Union
import pandas as pd
import tensorflow as tf

from src.encoder import Encoder
from src.entity import Entity
from src.triple import Triple
from src.link import Link


class Graph:
    def __init__(self, filepaths=None, encoder=None):
        self.filepaths: Union[list[str], None] = filepaths
        self.encoder: Encoder = encoder
        self.entities: Dict[str, Entity] = {}
        self.triples: list[Triple] = []
        self.links: list[Link] = []

    @staticmethod
    def from_csv(filepath):
        graph = Graph([filepath])
        df = pd.read_csv(filepath, sep=";")
        for i, row in df.iterrows():
            confidence = row["confidence"]
            subject_text = row["subject"]
            relation = row["relation"]
            object_text = row["object"]
            subject_id = row["subject_id"]
            object_id = row["object_id"]

            subject = graph.get_entity_by_id(subject_id, subject_text)
            object = graph.get_entity_by_id(object_id, object_text)
            graph.add_triple(subject, relation, object, confidence=confidence) 

        return graph

    def get_entity_by_id(self, entity_id, entity_text=""):
        if entity_id in self.entities:
            return self.entities[entity_id]
        return self.add_entity(entity_id, entity_text)
    
    def add_encoder(self, encoder):
        self.encoder = encoder

    def add_entity(self, id, text):
        new_entity = Entity(id, text)
        self.entities[id] = new_entity
        return new_entity

    def add_triple(self, subject, relation_text, object, confidence=1.0):
        new_triple = Triple(subject, relation_text, object, confidence=confidence)
        self.triples.append(new_triple)
        return new_triple

    def add_link(self, entity_a, entity_b):
        new_link = Link(entity_a, entity_b)
        self.links.append(new_link)
        return new_link

    def build_entity_encodings(self):
        subject_encodings, object_encodings = self.encoder.get_entity_encodings(self.triples)
        for triple, subject_encoding, object_encoding in zip(self.triples, subject_encodings, object_encodings):
            triple.subject.add_encoding(subject_encoding)
            triple.object.add_encoding(object_encoding)

    def build_links(self, threshold):
        self.links = []
        entities = list(self.entities.values())
        for i, entity_a in enumerate(entities):
            for entity_b in entities[i+1:]:
                normalized_a = tf.nn.l2_normalize(entity_a.encoding, 0)        
                normalized_b = tf.nn.l2_normalize(entity_b.encoding, 0)
                cosine = tf.reduce_sum(tf.multiply(normalized_a, normalized_b)).numpy()
                if cosine >= threshold:
                    self.add_link(entity_a, entity_b)
