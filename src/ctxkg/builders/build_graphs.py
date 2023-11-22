import traceback
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from tkinter import Tk
from tkinter.filedialog import askdirectory

from ..models.graph import Graph
from ..models.encoder import Encoder
from ...constants import TRIPLE_DIR, GRAPH_DIR
from ...utils.batch_data.helpers import set_batch_data, save_batch_params

from ...languages import Language


def build_graphs(language: Language, batch: str, size, ratio, threshold, batch_size):
    triple_dir = TRIPLE_DIR / language / batch
    kg_dir = GRAPH_DIR / language / batch
    kg_dir.mkdir(exist_ok=True)

    save_batch_params(language, batch, "base", {"size": size, "ratio": ratio, "threshold": threshold})

    base_dir = kg_dir / "base"
    base_dir.mkdir(exist_ok=True)
    errors_dir = base_dir / "errors"
    errors_dir.mkdir(exist_ok=True)

    graph_file_names = [f.stem for f in base_dir.glob("*.json")]
    remaining_files = [f for f in triple_dir.glob("*.csv") if f.stem not in graph_file_names]
    sorted_files = sorted(remaining_files, key=lambda file: file.stat().st_size)

    set_batch_data(language, batch, "base", "started")

    encoder = Encoder(size=size, language=language, ratio=ratio)
    failed_files = []
    for file in tqdm(sorted_files):
        try:
            graph = Graph.from_csv(file, encoder)
            graph.build_entity_encodings(batch_size)
            graph.build_links(threshold=threshold)
            graph.save_json(base_dir / f"{file.stem}.json")
        except KeyboardInterrupt:
            break
        except Exception:
            title = f"{datetime.now()}: {file.name}\n\n"
            log = traceback.format_exc()
            full_error = title + log
            failed_files.append(full_error)

    if len(failed_files) > 0:
        set_batch_data(language, batch, "base", "failed")
        with open(errors_dir / "failed_files.txt", "w", encoding="utf-8") as f:
            f.write("\n==========\n".join(failed_files))
    else:
        set_batch_data(language, batch, "base", "done")


if __name__ == "__main__":
    from .cli_args import SIZE, RATIO, THRESHOLD, LANGUAGE, NAME, BATCH_SIZE

    if LANGUAGE and NAME:
        batch_dir = TRIPLE_DIR / LANGUAGE / NAME
    else:
        base_dir = TRIPLE_DIR / LANGUAGE if LANGUAGE else TRIPLE_DIR
        Tk().withdraw()
        directory = askdirectory(initialdir=base_dir)
        batch_dir = Path(directory)

    language: Language = LANGUAGE if LANGUAGE else batch_dir.parent.name  # type: ignore
    batch = NAME if NAME else batch_dir.name

    build_graphs(SIZE, RATIO, THRESHOLD, language, batch, BATCH_SIZE)
