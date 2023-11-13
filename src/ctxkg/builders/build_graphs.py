import json
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from tkinter import Tk
from tkinter.filedialog import askopenfilenames, askdirectory

from ..models.graph import Graph
from ..models.encoder import Encoder
from ...constants import TRIPLE_DIR, GRAPH_DIR
from ...utils.batch_data import set_batch_data

from ...languages import Language


def build_graphs(language: Language, batch: str, size, ratio, threshold, batch_size):
    triple_dir = TRIPLE_DIR / language / batch
    kg_dir = GRAPH_DIR / language / batch
    kg_dir.mkdir(exist_ok=True)

    _save_params(kg_dir, size=size, ratio=ratio, threshold=threshold, batch_size=batch_size)

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
        except Exception as e:
            failed_files.append(f"{datetime.now()}: {file.name} - {e.__class__.__name__}: {e}")

    if len(failed_files) > 0:
        set_batch_data(language, batch, "base", "failed")
        with open(errors_dir / "failed_files.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(failed_files))
    else:
        set_batch_data(language, batch, "base", "done")


def _save_params(dir: Path, **kwargs):
    with (dir / "params.json").open("w", encoding="utf-8") as f:
        json.dump(kwargs, f, ensure_ascii=False, indent=2)


def _build_graphs_by_match(size, ratio, threshold, overwrite, match, name, batch_size):
    files = _get_files(match)

    kg_dir = GRAPH_DIR / name if name else _get_target_dir(GRAPH_DIR)
    kg_dir.mkdir(exist_ok=True)
    _save_params(kg_dir, size=size, ratio=ratio, threshold=threshold, batch_size=batch_size)

    base_dir = kg_dir / "base"
    base_dir.mkdir(exist_ok=True)
    errors_dir = base_dir / "errors"
    errors_dir.mkdir(exist_ok=True)

    filtered_files = [f for f in files if overwrite or not (base_dir / f"{f.stem}.json").is_file()]
    sorted_files = sorted(filtered_files, key=lambda file: file.stat().st_size)

    encoder = Encoder(size=size, ratio=ratio)
    failed_files = []
    for file in tqdm(sorted_files):
        try:
            graph = Graph.from_csv(file, encoder)
            graph.build_entity_encodings(batch_size)
            graph.build_links(threshold=threshold)
            graph.save_json(base_dir / f"{file.stem}.json")
        except KeyboardInterrupt:
            break
        except Exception as e:
            failed_files.append(f"{datetime.now()}: {file.name} - {e.__class__.__name__}: {e}")

    with open(errors_dir / "failed_files.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(failed_files))

    return kg_dir


def _get_target_dir(base_dir):
    window = Tk()
    window.withdraw()
    window.attributes("-topmost", 1)
    directory = askdirectory(initialdir=base_dir)
    return Path(directory)


def _get_files(match):
    if match is None:
        Tk().withdraw()
        filenames = askopenfilenames(initialdir=TRIPLE_DIR)
        filepaths = [Path(f) for f in filenames]
    else:
        filepaths = list(TRIPLE_DIR.glob(match))
    return [f for f in filepaths if f.suffix == ".csv" and f.is_file()]


if __name__ == "__main__":
    from .cli_args import SIZE, RATIO, THRESHOLD, OVERWRITE, MATCH, NAME, BATCH
    _build_graphs_by_match(SIZE, RATIO, THRESHOLD, OVERWRITE, MATCH, NAME, BATCH)
