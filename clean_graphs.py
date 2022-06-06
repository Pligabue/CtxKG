from pathlib import Path

from src.graph import Graph
from constants import RESULT_DIR
from cli_args import MATCH


def main(match):
    dirs = [dir for dir in RESULT_DIR.glob(match) if dir.is_dir()]

    for dir in dirs:
        base_dir = dir / "base"
        clean_dir = dir / "clean"
        clean_dir.mkdir(exist_ok=True)
        
        for file in base_dir.glob("*.json"):
            graph = Graph.from_json(file)
            graph.clean()
            graph.save_json(clean_dir / file.name)

if __name__ == "__main__":
    main(MATCH)