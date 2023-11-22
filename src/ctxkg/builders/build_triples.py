import subprocess
from triple_extractor_ptbr_pligabue.model import TripleExtractor

from .constants import OPEN_IE_DIR, OPEN_IE_SOURCE_DIR, OPEN_IE_JAR
from ...constants import (ENGLISH_PREFIX, PORTUGUESE_PREFIX, DOCUMENT_DIR, TRIPLE_DIR,
                          ENGLISH_DOC_DIR, PORTUGUESE_DOC_DIR, PORTUGUESE_TRIPLE_DIR)
from ...utils.batch_data.helpers import set_batch_data

from ...languages import Language
from ...utils.batch_data.types import BatchStatus


def build_triples(language: Language, batch: str):
    _setup_directories()

    if language == ENGLISH_PREFIX:
        _build_triples_en([batch])
    elif language == PORTUGUESE_PREFIX:
        _build_triples_pt_BR([batch])


def _setup_directories(reference_dir=DOCUMENT_DIR, target_dir=TRIPLE_DIR):
    subdirectories = [f for f in reference_dir.iterdir() if f.is_dir()]
    for subdir in subdirectories:
        target_subdir = target_dir / subdir.name
        target_subdir.mkdir(exist_ok=True)
        _setup_directories(subdir, target_subdir)


def _build_triples_en(batches: list[str]):
    batches = batches if len(batches) > 0 else [p.name for p in ENGLISH_DOC_DIR.iterdir() if p.is_dir()]

    _set_multiple_batches("en", batches, "started")

    try:
        source_last_mod = max([f.stat().st_mtime for f in OPEN_IE_SOURCE_DIR.glob("*.java")])
        target_last_mod = OPEN_IE_JAR.exists() and OPEN_IE_JAR.stat().st_mtime
        if source_last_mod > target_last_mod:
            subprocess.run(["mvn", "compile", "assembly:single"], cwd=OPEN_IE_DIR, shell=True, check=True)
        subprocess.run(["java", "-cp", str(OPEN_IE_JAR), "com.triplebuilder.app.TripleBuilder", *batches])

        _set_multiple_batches("en", batches, "done")
    except subprocess.CalledProcessError:
        print("Error compiling Java code.")
    except Exception:
        _set_multiple_batches("en", batches, "failed")


def _build_triples_pt_BR(batches: list[str]):
    batches = batches if len(batches) > 0 else [p.name for p in PORTUGUESE_DOC_DIR.iterdir() if p.is_dir()]

    _set_multiple_batches("pt-BR", batches, "started")

    try:
        triple_extractor = TripleExtractor.load()

        for batch in batches:
            source_dir = PORTUGUESE_DOC_DIR / batch
            doc_paths = list(source_dir.glob("*.txt"))
            target_dir = PORTUGUESE_TRIPLE_DIR / batch
            target_dir.mkdir(exist_ok=True)

            triple_extractor.process_docs(doc_paths, target_dir)

        _set_multiple_batches("pt-BR", batches, "done")
    except Exception:
        _set_multiple_batches("pt-BR", batches, "failed")


def _set_multiple_batches(language: Language, batches: list[str], status: BatchStatus):
    for batch in batches:
        set_batch_data(language, batch, "triples", status)


if __name__ == "__main__":
    from .cli_args import LANGUAGE, NAME

    if LANGUAGE and NAME:
        build_triples(LANGUAGE, NAME)
    else:
        _setup_directories()

        if LANGUAGE == "en":
            _build_triples_pt_BR([])
        elif LANGUAGE == "pt-BR":
            _build_triples_pt_BR([])
        else:
            _build_triples_en([])
            _build_triples_pt_BR([])
