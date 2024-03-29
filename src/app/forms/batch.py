from flask import request
from wtforms import (Form, StringField, SelectField, IntegerField, FloatField, MultipleFileField, HiddenField,
                     ValidationError)
from wtforms.validators import InputRequired, AnyOf, NumberRange
from triple_extractor_ptbr_pligabue.constants import MODEL_DIR

from ...utils.batch_data.helpers import get_batch_list
from ...constants import DEFAULT_PARAMS


class BatchForm(Form):
    name = StringField("Batch name", [InputRequired()])
    language = HiddenField("Language", [AnyOf(["en", "pt-BR"])])
    bert_size = SelectField("Bert size", default="small",
                            choices=[("small", "Small"), ("medium", "Medium"), ("big", "Big")])
    extraction_model = SelectField("Triple extraction model", default="default",
                                   choices=[(path.name, path.stem) for path in MODEL_DIR.iterdir() if path.is_dir()])
    filenames = MultipleFileField("Text files")
    embedding_ratio = FloatField("Embedding ratio", [NumberRange(0.0, 1.0)], default=DEFAULT_PARAMS["base"]["ratio"])
    similarity_threshold = FloatField("Similarity coef. (synonyms)", [NumberRange(0.0, 1.0)],
                                      default=DEFAULT_PARAMS["base"]["threshold"])
    bridge_threshold = FloatField("Similarity coef. (bridges)", [NumberRange(0.0, 1.0)],
                                  default=DEFAULT_PARAMS["bridges"]["threshold"])
    processing_batch_size = IntegerField("Processing batch size", default=DEFAULT_PARAMS["base"]["batch_size"])

    def show_bert_size(self):
        return self.language.data == "en"

    def show_extraction_model(self):
        return self.language.data == "pt-BR"

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

        existing_batch_names = [batch["name"] for batch in get_batch_list(language)]  # type: ignore
        if field.data in existing_batch_names:
            raise ValidationError(f"\"{field.data}\" is taken. Choose a different name.")

    def validate_filenames(self, _):
        if len(request.files) < 1:
            raise ValidationError("A text file is required.")
