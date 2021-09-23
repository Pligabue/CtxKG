import subprocess

def main():
    subprocess.run(["javac", "-cp", ".\open_ie\stanford-corenlp-4.2.2\*", ".\open_ie\TripleBuilder.java"])
    subprocess.run(["java", "-cp", ".\open_ie\stanford-corenlp-4.2.2\*;.\open_ie", "TripleBuilder"])

if __name__ == "__main__":
    main()