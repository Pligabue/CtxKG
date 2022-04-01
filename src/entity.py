

class Entity:
    def __init__(self, id: str, text: str):
        self.id = id
        self.text = text
        self.encoding = None
        self.encoding_count = 0

    def add_encoding(self, encoding):
        if self.encoding_count == 0:
            self.encoding = encoding
        else:
            self.encoding = (self.encoding * self.encoding_count + encoding) / (self.encoding_count + 1)
        self.encoding_count += 1

    def __repr__(self):
        return f'<Entity "{self.text}">'