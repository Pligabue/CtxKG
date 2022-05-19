from pathlib import Path
import json

from tqdm import tqdm

from src.graph import Graph
from src.encoder import Encoder
from cli_args import GROUPS, MATCH, SIZE, RATIO, THRESHOLD, CLEAN


def read_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize(bridge_dir, graph_files):
    reversed_files = [bridge_dir / file.name for file in graph_files[::-1]]
    for file in reversed_files[:-1]:
        bridges = read_json(file)
        for target_file in reversed_files[reversed_files.index(file)+1:]:
            target_bridges = read_json(target_file)
            bridges[target_file.name] = {value: key for key, value in target_bridges[file.name].items()}
        with file.open("w", encoding="utf-8") as f:
            json.dump(bridges, f, indent=2)

def main():
    RESULT_DIR = Path('./results')
    KG_NODE_DIRS = [path for path in RESULT_DIR.glob(MATCH) if path.is_dir()]

    encoder = Encoder(size=SIZE)

    for dir in KG_NODE_DIRS:
        graph_dir = dir / "clean" if CLEAN else dir / "base"
        bridge_dir = graph_dir / "bridges"
        bridge_dir.mkdir(exist_ok=True)
        
        graph_files = list(graph_dir.glob("*.json"))
        for graph_file in tqdm(graph_files):
            bridges = {}
            for target_graph_file in graph_files[graph_files.index(graph_file)+1:]:
                graph = Graph.from_json(graph_file).add_encoder(encoder).build_entity_encodings()
                target_graph = Graph.from_json(target_graph_file).add_encoder(encoder).build_entity_encodings()
                entities = graph.entities.values()
                target_entities = target_graph.entities.values()
                bridges[target_graph_file.name] = {e.id: te.id for e in entities for te in target_entities if e.id == te.id or e.compare(te) > THRESHOLD}
            with (bridge_dir / graph_file.name).open("w", encoding="utf-8") as f:
                json.dump(bridges, f, indent=2)

        normalize(bridge_dir, graph_files)

if __name__ == "__main__":
    main()