from multiprocessing import Process

from typing import get_args

from ...ctxkg.builders.runner import run
from ...utils.batch_data.helpers import get_metadata, set_batch_data, get_batch_params

from ...languages import Language
from ...utils.batch_data.types import Stage


def resume_processing(language: Language, batch: str):
    metadata = get_metadata()[language][batch]

    for stage in get_args(Stage):
        if metadata[stage] == "paused":
            set_batch_data(language, batch, stage, "pending")

    params = get_batch_params(language, batch)
    size = params["base"]["size"]
    ratio = params["base"]["ratio"]
    similarity_threshold = params["base"]["threshold"]
    bridge_threshold = params["bridges"]["threshold"]
    batch_size = params["base"]["batch_size"]

    p = Process(
        target=run,
        args=(language, batch, size, ratio, similarity_threshold, bridge_threshold, batch_size),
        name=f"Creating batch {batch}"
    )
    p.start()
