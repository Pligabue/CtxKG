from pathlib import Path

from .utils.batch_data.types import BatchParams
from .languages import English, Portuguese


BASE_PATH = Path()

METADATA_PATH = BASE_PATH / "metadata.json"

ENGLISH_PREFIX: English = "en"
PORTUGUESE_PREFIX: Portuguese = "pt-BR"

DOCUMENT_DIR = BASE_PATH / "documents"
ENGLISH_DOC_DIR = DOCUMENT_DIR / ENGLISH_PREFIX
PORTUGUESE_DOC_DIR = DOCUMENT_DIR / PORTUGUESE_PREFIX

TRIPLE_DIR = BASE_PATH / "triples"
ENGLISH_TRIPLE_DIR = TRIPLE_DIR / ENGLISH_PREFIX
PORTUGUESE_TRIPLE_DIR = TRIPLE_DIR / PORTUGUESE_PREFIX

GRAPH_DIR = BASE_PATH / "graphs"
ENGLISH_GRAPH_DIR = GRAPH_DIR / ENGLISH_PREFIX
PORTUGUESE_GRAPH_DIR = GRAPH_DIR / PORTUGUESE_PREFIX
BLABKG_DIR = ENGLISH_GRAPH_DIR / "BlabKG"

DEFAULT_PARAMS: BatchParams = {
    "base": {
        "size": "small",
        "ratio": 1.0,
        "threshold": 0.8,
        "batch_size": 300,
    },
    "bridges": {
        "size": "small",
        "ratio": 1.0,
        "threshold": 0.7,
        "batch_size": 300,
    },
}
