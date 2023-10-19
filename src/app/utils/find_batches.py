from typing import TypedDict, Literal

from ...constants import DOCUMENT_DIR, TRIPLE_DIR, GRAPH_DIR, BLABKG_DIR


BatchStatus = Literal["done", "pending", "failed"]


class Batch(TypedDict):
    name: str
    triples: BatchStatus
    base: BatchStatus
    clean: BatchStatus
    bridges: BatchStatus


def find_batches(language: str):
    doc_dir = DOCUMENT_DIR / language
    triple_dir = TRIPLE_DIR / language
    graph_dir = GRAPH_DIR / language
    all_dirs = [doc_dir, triple_dir, graph_dir]
    batch_names = {path.stem for dir in all_dirs for path in dir.iterdir() if path.is_dir()}

    batches: list[Batch] = []
    for batch_name in batch_names:
        triple = (TRIPLE_DIR / language / batch_name).exists()
        base = (GRAPH_DIR / language / batch_name / "base").exists()
        clean = (GRAPH_DIR / language / batch_name / "clean").exists()
        bridges = (GRAPH_DIR / language / batch_name / "bridges").exists()

        batches.append({
            "name": batch_name,
            "triples": "done" if triple else "pending" if not (base or clean or bridges) else "failed",
            "base": "done" if base else "pending" if not (clean or bridges) else "failed",
            "clean": "done" if clean else "pending" if not bridges else "failed",
            "bridges": "done" if bridges else "pending",
        })

    sorted_batches = sorted(batches, key=batch_priority, reverse=True)

    return sorted_batches


def batch_priority(batch: Batch):
    return (
        batch["name"] == BLABKG_DIR.stem,
        batch["bridges"] == "done",
        batch["clean"], batch["base"] == "done",
        batch["triples"] == "done",
    )
