# CtxKG - Context-Based Knowledge Graph

## Introduction

CtxKG is our method for generating knowledge graphs directly from text. Its goal is to process multiple documents in order to create graphs for each one, which are then combined to form a connected network that functions as one single graph.

It contains four stages—triple generation, graph generation, graph reduction and bridge building—and is available in both English and Portuguese.

It is based on AutoKG[^1] and it uses CoreNLP's OpenIE implementation[^2], our own OpenIE implementation for Portuguese[^3], BERT[^4] and BERTimbau[^5].

## Usage

### Prerequisites

We recommend that you use Python `3.9` (though `3.10` and `3.11` should also work) and that you have [Poetry](https://python-poetry.org/) installed. 

### Installing

```sh
poetry install
```

### Running the server

The server is the main way to run and manage the knowledge graph generation process.

Start the Flask server by running:
```sh
flask --app src.app run
```

For the debug mode, run:
```sh
flask --app src.app run --debug
```

The application contains x main sections:

- The **home page**, where you can choose between the English and the Portuguese version.
- The **batch page**, where you can see all batches that have been created for that language, as well as create a new batch.
- The **graph list pages**, where you can see the list of graphs (both base and reduced) that have been created for a batch.
- The **graph display page**, where graphs can be inspected visually, with nodes/entities being represented by circles and edges/relationships being represented by lines.

### Running specific stages

If you wish, you may run any of the four stages directly from the CLI. This is done by calling any of the four modules using `python -m` and passing the relevant CLI arguments.

#### Setting up the documents

To correctly set up the documents for the knowledge graph generation, you must add all TXT files to the `documents` directory, within your desired language, inside a folder with the name you want for your document group. For example, if you have a set of documents in English about history, you should create a new directory named `History` inside the `documents / en` directory and create copies of your documents in it. 

#### Generate triples

Once the documents are in the correct directory, you may run `python -m src.ctxkg.builders.build_triples` to convert each document into a set of relationship triples. The triples are stored in the `triples` directory. You may include the following CLI arguments:

- `-l`/`--language`: the language of the documents you want to process. Can be either `en` or `pt-BR`, depending on where the documents are. Not passing this argument will cause all documents in both languages to be processed.
- `-n`/`--name`: name of the group (e.g. `History` in the last example). Must be within the selected language's directory. Not passing this argument will cause all documents within the selected language to be processed.

#### Build knowledge graphs

With the generated triples, building the base knowledge graphs is done by running `python -m src.ctxkg.builders.build_graphs`. You may include the following CLI arguments:
- `--small`/`--medium`/`--big`: the size of the BERT encoder (English only). Defaults to `small`.
- `-t`/`--threshold`: the minimum cosine similarity for two entities to be considered synonyms. Defaults to `0.8`.
- `-r`/`--ratio`: the ratio between the base entity encoding and the triple encoding for the generation of the final entity encoding. Defaults to `1.0` (i.e. only base entity encoding).
- `-l`/`--language`: the language of the documents you want to process. Can be either `en` or `pt-BR`, depending on where the documents are. If not set, a dialog will open and request that you select a group.
- `-n`/`--name`: name of the group you want to process. If not set, a dialog will open and request that you select one.
- `-b`/`--batch`: impacts how many entity encodings at processed at a time by the GPU. Defaults to `300`. Probably will not need to be changed.

#### Reduce graphs

To run the graph reduction stage, execute `python -m src.ctxkg.builders.clean_graphs`. In this stage, synonyms are merged into a single entity, which is the one among the synonyms that is the most recurring in the graph. You may include the following CLI arguments:

- `-l`/`--language`: the language of the graph group you want to reduce. Can be either `en` or `pt-BR`, depending on where the documents are. If not set, a dialog will open and request that you select the group directory.
- `-n`/`--name`: name of the group. If not set, a dialog will open and request that you select the group directory.

#### Build bridges

To generate connections between different graphs, run `python -m src.ctxkg.builders.build_bridges`. This is the most time-consuming step, as all individual graphs are compared to each other. You may include the following CLI arguments:

- `--small`/`--medium`/`--big`: the size of the BERT encoder (English only). Defaults to `small`.
- `-t`/`--threshold`: the minimum cosine between two entities for a bridge to be established. Defaults to `0.8`.
- `-r`/`--ratio`: the ratio between the base entity encoding and the triple encoding for the generation of the final entity encoding. Defaults to `1.0` (i.e. only base entity encoding).
- `-l`/`--language`: the language of the graph group you want to reduce. Can be either `en` or `pt-BR`, depending on where the documents are. If not set, a dialog will open and request that you select the group directory.
- `-n`/`--name`: name of the group. If not set, a dialog will open and request that you select the group directory.

## References

[^1]: https://arxiv.org/abs/2008.08995
[^2]: https://stanfordnlp.github.io/CoreNLP/
[^3]: https://github.com/Pligabue/PTBR-OpenIE
[^4]: https://arxiv.org/abs/1810.04805
[^5]: https://huggingface.co/neuralmind/bert-base-portuguese-cased