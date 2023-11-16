from typing import Optional

from ...languages import Language
from ...utils.batch_data import Stage


def run(language: Language, batch: str, size: str, ratio: float,
        similarity_threshold: float, bridge_threshold: float, batch_size: int):
    from .build_triples import build_triples
    from .build_graphs import build_graphs
    from .clean_graphs import clean_batch
    from .build_bridges import build_bridges

    if _should_run_stage(language, batch, "triples"):
        build_triples(language, batch)
    if _should_run_stage(language, batch, "base", "triples"):
        build_graphs(language, batch, size, ratio, similarity_threshold, batch_size)
    if _should_run_stage(language, batch, "clean", "base"):
        clean_batch(language, batch)
    if _should_run_stage(language, batch, "bridges", "clean"):
        build_bridges(language, batch, size, ratio, bridge_threshold)


def _should_run_stage(language: Language, batch: str, stage: Stage, previous_stage: Optional[Stage] = None):
    from ...utils.batch_data import get_metadata

    batch_data = get_metadata()[language][batch]
    already_started = batch_data[stage] == "started"
    previous_stage_succeeded = previous_stage is None or batch_data[previous_stage] == "done"
    is_pending = batch_data[stage] == "pending"
    can_start = previous_stage_succeeded and is_pending

    return can_start or already_started
