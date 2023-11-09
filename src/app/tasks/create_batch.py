from multiprocessing import Process

from ...ctxkg.builders.runner import run

from ...languages import Language


def create_batch(language: Language, batch: str, filepaths: list[str], size: str, ratio: float,
                 similarity_threshold: float, bridge_threshold: float, batch_size: int):
    p = Process(
        target=run,
        args=(language, batch, filepaths, size, ratio, similarity_threshold, bridge_threshold, batch_size),
        name=f"Creating batch {batch}"
    )
    p.start()
