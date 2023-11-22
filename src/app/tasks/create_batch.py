from multiprocessing import Process
from werkzeug.datastructures.file_storage import FileStorage

from ...constants import DOCUMENT_DIR
from ...ctxkg.builders.runner import run
from ...utils.batch_data.helpers import set_batch_data

from ...languages import Language


def create_batch(language: Language, batch: str, files: list[FileStorage], size: str, ratio: float,
                 similarity_threshold: float, bridge_threshold: float, batch_size: int):
    _setup_docs(language, batch, files)
    p = Process(
        target=run,
        args=(language, batch, size, ratio, similarity_threshold, bridge_threshold, batch_size),
        name=f"Creating batch {batch}"
    )
    p.start()


def _setup_docs(language: Language, name: str, files: list[FileStorage]):
    batch_dir = DOCUMENT_DIR / language / name
    if batch_dir.exists():
        return
    batch_dir.mkdir()

    set_batch_data(language, name, "triples", "pending")

    for file in files:
        target_file = batch_dir / file.filename  # type: ignore
        file.save(target_file)
