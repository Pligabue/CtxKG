import tensorflow as tf

from typing import Optional


class Entity:
    def __init__(self, id: str, text: str):
        self.id = id
        self.text = text
        self.encoding: Optional[tf.Tensor] = None
        self.encoding_count = tf.constant(0, dtype=float)

    def add_encoding(self, encoding):
        if self.encoding is None:
            self.encoding = encoding
        else:
            self.encoding = (self.encoding * self.encoding_count + encoding) / (self.encoding_count + 1)
        self.encoding_count += 1

    def is_named_entity(self):
        return self.id.startswith("NE-")

    def compare(self, other: "Entity"):
        return tf.tensordot(tf.math.l2_normalize(self.encoding, 0), tf.math.l2_normalize(other.encoding, 0), 1).numpy()

    def __repr__(self):
        return f'<Entity "{self.text}">'
