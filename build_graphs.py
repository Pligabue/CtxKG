from pathlib import Path
from datetime import datetime
from tqdm import tqdm
from tkinter import Tk
from tkinter.filedialog import askopenfilenames, askdirectory

from src.graph import Graph
from src.encoder import Encoder

from constants import TRIPLE_DIR, RESULT_DIR
from cli_args import SIZE, RATIO, THRESHOLD, OVERWRITE, MATCH, NAME, BATCH


def get_target_dir(base_dir):
    window = Tk()
    window.withdraw()
    window.attributes("-topmost", 1)
    directory = askdirectory(initialdir=base_dir)
    return Path(directory)

def get_files(match):
    if match is None:
        Tk().withdraw()
        filenames = askopenfilenames(initialdir=TRIPLE_DIR)
        filepaths = [Path(f) for f in filenames]
    else:
        filepaths = list(TRIPLE_DIR.glob(match))
    return [f for f in filepaths if f.suffix == ".csv" and f.is_file()]

def save_params(dir: Path, size, ratio, threshold, overwrite, match, name, batch_size):
    with (dir / "PARAMS.md").open("w", encoding="utf-8") as f:
        params = (f"BERT SIZE: {size}\n" \
                  f"RATIO (entity encoding over full sentence encoding): {ratio}\n" \
                  f"THRESHOLD: {threshold}\n" \
                  f"OVERWRITE: {overwrite}\n" \
                  f"FILE NAME MATCHING: {match}\n" \
                  f"GROUP NAME: {name}\n" \
                  f"ENCODING BATCH SIZE: {batch_size}\n")
        f.write(params)

def main(size, ratio, threshold, overwrite, match, name, batch_size):
    files = get_files(match)

    kg_dir = RESULT_DIR / name if name else get_target_dir(RESULT_DIR)
    kg_dir.mkdir(exist_ok=True)
    save_params(kg_dir, size, ratio, threshold, overwrite, match, name, batch_size)

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

if __name__ == "__main__":
    main(SIZE, RATIO, THRESHOLD, OVERWRITE, MATCH, NAME, BATCH)