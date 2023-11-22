from typing import TypedDict, Literal

from ...languages import Language


Stage = Literal["triples", "base", "clean", "bridges"]
BatchStatus = Literal["done", "started", "pending", "paused", "failed"]


class Batch(TypedDict):
    triples: BatchStatus
    base: BatchStatus
    clean: BatchStatus
    bridges: BatchStatus


BatchDataMap = dict[str, Batch]
BatchMetadata = dict[Language, BatchDataMap]


class BatchListItem(TypedDict):
    name: str
    triples: BatchStatus
    base: BatchStatus
    clean: BatchStatus
    bridges: BatchStatus
    can_be_paused: bool
    can_be_resumed: bool


class BlabKGException(Exception):
    pass
