from typing import get_args

from ...utils.batch_data.helpers import get_metadata, set_batch_data

from ...languages import Language


def startup():
    _pause_interrupted_processes()


def _pause_interrupted_processes():
    metadata = get_metadata()
    for language in get_args(Language):
        batches = metadata[language]
        for batch, batch_data in batches.items():
            for stage, status in batch_data.items():
                if status == "started":
                    set_batch_data(language, batch, stage, "paused")  # type: ignore
