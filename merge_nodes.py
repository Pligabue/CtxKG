from pathlib import Path

def main():
    CURRENT_DIR = Path()
    dirs = [dir for dir in CURRENT_DIR.glob("kg_nodes*") if dir.is_dir()]

    for dir in dirs:
        nodes = []
        for file in dir.glob("*.txt"):
            with open(file) as f:
                for line in f:
                    node = line.strip()
                    nodes.append(node)

        nodes.sort(key=str.casefold)
        merged_node_text = "\n".join(nodes)

        with open(f"results/{dir.name}.summary.txt", "w", encoding="utf-8") as f:
            f.write(merged_node_text)

if __name__ == "__main__":
    main()