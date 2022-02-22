import subprocess
from pathlib import Path


def main():
    OPEN_IE_DIR = Path("./open_ie")
    try:
        stanford_lib_name = next(OPEN_IE_DIR.glob("stanford-corenlp-*")).name
        subprocess.run(["javac", "-cp", f".\open_ie\{stanford_lib_name}\*", ".\open_ie\TripleBuilder.java"])
        subprocess.run(["java", "-cp", f".\open_ie\{stanford_lib_name}\*;.\open_ie", "-Dfile.encoding=UTF8", "TripleBuilder"])
    except StopIteration:
        raise "Stanford's CoreNLP library missing."


if __name__ == "__main__":
    main()