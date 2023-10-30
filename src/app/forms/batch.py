from wtforms import (Form, StringField, SelectField, IntegerField, FloatField, MultipleFileField, HiddenField,
                     ValidationError)
from wtforms.validators import InputRequired, AnyOf, NumberRange

from ..utils.batch_data import get_batch_data


class BatchForm(Form):
    name = StringField("Batch name", [InputRequired()])
    language = HiddenField("Language", [AnyOf(["en", "pt-BR"])])
    bert_size = SelectField("Bert size", choices=[("small", "Small"), ("medium", "Medium"), ("big", "Big")])
    filenames = MultipleFileField("Text files", [InputRequired()])
    embedding_ratio = FloatField("Embedding ratio", [NumberRange(0.0, 1.0)], default=1.0)
    similarity_threshold = FloatField("Similarity coef. (synonyms)", [NumberRange(0.0, 1.0)], default=0.8)
    bridge_threshold = FloatField("Similarity coef. (bridges)", [NumberRange(0.0, 1.0)], default=0.7)
    processing_batch_size = IntegerField("Processing batch size", default=300)

    def show_advanced_options(self):
        return (
            self.embedding_ratio.data != self.embedding_ratio.default
            or self.similarity_threshold.data != self.similarity_threshold.default
            or self.bridge_threshold.data != self.bridge_threshold.default
            or self.processing_batch_size.data != self.processing_batch_size.default
        )

    def validate_name(self, field):
        language = self.language.data
        if not language:
            return

        existing_batch_names = [batch["name"] for batch in get_batch_data(language)]
        if field.data in existing_batch_names:
            raise ValidationError("Name has been selected. Choose a different one.")
