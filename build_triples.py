import subprocess

subprocess.run(["javac", "-cp", f'".\open_ie\stanford-corenlp-4.2.2\*"', ".\open_ie\TripleBuilder.java"])
subprocess.run(["java", "-cp", f'".\open_ie\stanford-corenlp-4.2.2\*;.\open_ie"', "TripleBuilder"])