import json
from pathlib import Path
import shutil

from typing import TypedDict, Literal

from ..constants import METADATA_PATH, ENGLISH_PREFIX, PORTUGUESE_PREFIX
from ..constants import DOCUMENT_DIR, TRIPLE_DIR, GRAPH_DIR, BLABKG_DIR

from ..languages import Language


Stage = Literal["triples", "base", "clean", "bridges"]
BatchStatus = Literal["done", "started", "pending", "failed"]


class Batch(TypedDict):
    triples: BatchStatus
    base: BatchStatus
    clean: BatchStatus
    bridges: BatchStatus


BatchDataMap = dict[str, Batch]
BatchMetadata = dict[Language, BatchDataMap]


def get_metadata() -> BatchMetadata:
    if METADATA_PATH.exists():
        with METADATA_PATH.open(encoding="utf-8") as f:
            return json.load(f)

    metadata = _build_metadata()
    _write_metadata(metadata)

    return metadata


class BatchListItem(TypedDict):
    name: str
    triples: BatchStatus
    base: BatchStatus
    clean: BatchStatus
    bridges: BatchStatus


def get_batch_list(language: Language):
    metadata = get_metadata()
    batch_names = metadata[language].keys()

    batches: list[BatchListItem] = []
    for batch in batch_names:
        batches.append({
            "name": batch,
            "triples": metadata[language][batch]["triples"],
            "base": metadata[language][batch]["base"],
            "clean": metadata[language][batch]["clean"],
            "bridges": metadata[language][batch]["bridges"],
        })

    sorted_batches = sorted(batches, key=_batch_priority, reverse=True)

    return sorted_batches


def set_batch_data(language: Language, batch: str, stage: Stage, status: BatchStatus):
    metadata = get_metadata()

    if language not in metadata:
        metadata[language] = {}
    if batch not in metadata[language]:
        metadata[language][batch] = {
            "triples": "pending",
            "base": "pending",
            "clean": "pending",
            "bridges": "pending",
        }
    metadata[language][batch][stage] = status
    _write_metadata(metadata)


class BlabKGException(Exception):
    pass


def delete_batch(language: Language, batch: str):
    doc_dir = DOCUMENT_DIR / language / batch
    triple_dir = TRIPLE_DIR / language / batch
    graph_dir = GRAPH_DIR / language / batch

    if graph_dir == BLABKG_DIR:
        raise BlabKGException("Can't delete the official BlabKG graphs.")

    shutil.rmtree(doc_dir, ignore_errors=True)
    shutil.rmtree(triple_dir, ignore_errors=True)
    shutil.rmtree(graph_dir, ignore_errors=True)

    metadata = get_metadata()
    if metadata[language] and metadata[language][batch]:
        del metadata[language][batch]
    _write_metadata(metadata)


def _build_metadata():
    metadata = {}

    for language in [ENGLISH_PREFIX, PORTUGUESE_PREFIX]:
        metadata[language] = {}

        doc_dir = DOCUMENT_DIR / language
        triple_dir = TRIPLE_DIR / language
        graph_dir = GRAPH_DIR / language
        all_dirs = [doc_dir, triple_dir, graph_dir]
        batch_names = {path.stem for dir in all_dirs for path in dir.iterdir() if path.is_dir()}

        for batch_name in batch_names:
            batch_doc_dir = doc_dir / batch_name
            if not batch_doc_dir.exists():
                batch_doc_dir.mkdir()

            batch_triple_dir = triple_dir / batch_name
            batch_base_dir = graph_dir / batch_name / "base"
            batch_clean_dir = graph_dir / batch_name / "clean"
            batch_bridge_dir = graph_dir / batch_name / "bridges"

            metadata[language][batch_name] = {
                "triples": _get_stage_status(batch_doc_dir, batch_triple_dir),
                "base": _get_stage_status(batch_doc_dir, batch_base_dir),
                "clean": _get_stage_status(batch_doc_dir, batch_clean_dir),
                "bridges": _get_stage_status(batch_doc_dir, batch_bridge_dir),
            }

    return metadata


def _get_stage_status(doc_dir: Path, target_dir: Path) -> BatchStatus:
    if not target_dir.exists():
        return "pending"

    doc_set = {path.stem for path in doc_dir.iterdir() if path.is_file()}
    target_set = {path.stem for path in target_dir.iterdir() if path.is_file()}
    missing = doc_set - target_set

    if len(missing) == 0:
        return "done"
    if len(missing) < len(doc_set):
        return "started"
    return "failed"


def _write_metadata(metadata):
    with METADATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def _batch_priority(batch: BatchListItem):
    return (
        batch["name"] == BLABKG_DIR.stem,
        batch["bridges"] == "done",
        batch["clean"] == "done",
        batch["base"] == "done",
        batch["triples"] == "done",
    )
