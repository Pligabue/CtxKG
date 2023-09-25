import json
from pprint import pp
import re
import statistics
from collections import Counter

from src.ctxkg.builders.constants import GRAPH_DIR


blab_dir = GRAPH_DIR / "BLAB"
base_dir = blab_dir / "base"
clean_dir = blab_dir / "clean"
bridge_dir = clean_dir / "bridges"


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def take_top_entries(count, n):
    items = sorted(count.items(), key=lambda count: count[1], reverse=True)
    top_n_items = items[:n]
    return dict(top_n_items)


def get_type(entity_id):
    m = re.match(r"NE-(?P<type>[^-]+)-.*", entity_id)
    return m["type"] if m else None


def is_ne(entity_id):
    return get_type(entity_id) is not None


def is_ne_ne(bridge):
    return is_ne(bridge[0]) and is_ne(bridge[1])


def is_ne_re(bridge):
    return (is_ne(bridge[0]) and not is_ne(bridge[1])) or (not is_ne(bridge[0]) and is_ne(bridge[1]))


def is_re_re(bridge):
    return not is_ne(bridge[0]) and not is_ne(bridge[1])


def get_regular_entity_text(entity_id):
    return re \
        .sub(r"-\d+-?", " ", re.sub(r"[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}-", "", entity_id)) \
        .strip() \
        .lower()


def get_named_entity_text(entity_id):
    return re.sub(r"-\d+-?", " ", re.sub(r"NE-[A-Z]+-", "", entity_id)).strip().lower()


def get_text(entity_id):
    return get_named_entity_text(entity_id) if is_ne(entity_id) else get_regular_entity_text(entity_id)


def entity_contains_the_other(bridge):
    entity_a, entity_b = bridge
    return get_text(entity_a) in get_text(entity_b) or get_text(entity_b) in get_text(entity_a)


def graph_eval(graph_dir, top_n=20):
    graphs = [read_json(graph_path) for graph_path in graph_dir.glob("*.json")]
    entity_sets = [graph["entities"] for graph in graphs]
    named_entity_sets = [
        {id: text for id, text in e_set.items() if id.startswith("NE-")} for e_set in entity_sets
    ]
    unnamed_entity_sets = [
        {id: text for id, text in e_set.items() if not id.startswith("NE-")} for e_set in entity_sets
    ]
    relationship_sets = [graph["graph"] for graph in graphs]
    synonym_sets = [graph["links"] for graph in graphs]

    # Table 1
    entity_set_sizes = [len(entitys_set) for entitys_set in entity_sets]
    entity_set_total = sum(entity_set_sizes)
    entity_set_avg = statistics.mean(entity_set_sizes)
    entity_set_stdev = statistics.stdev(entity_set_sizes)

    named_entity_set_sizes = [len(named_entity_set) for named_entity_set in named_entity_sets]
    named_entity_set_total = sum(named_entity_set_sizes)
    named_entity_set_avg = statistics.mean(named_entity_set_sizes)
    named_entity_set_stdev = statistics.stdev(named_entity_set_sizes)

    relationship_set_sizes = [len(relationship_set) for relationship_set in relationship_sets]
    relationship_set_total = sum(relationship_set_sizes)
    relationship_set_avg = statistics.mean(relationship_set_sizes)
    relationship_set_stdev = statistics.stdev(relationship_set_sizes)

    synonym_set_sizes = [
        len([syn for synonym_list in synonym_set.values() for syn in synonym_list]) / 2 for synonym_set in synonym_sets
    ]
    synonym_set_total = sum(synonym_set_sizes)
    synonym_set_avg = statistics.mean(synonym_set_sizes)
    synonym_set_stdev = statistics.stdev(synonym_set_sizes)

    # Table 2
    named_entity_count = Counter(
        [text.lower() for named_entity_set in named_entity_sets for text in named_entity_set.values()]
    )
    named_entities_top = take_top_entries(named_entity_count, top_n)

    # Table 3
    unnamed_entity_count = Counter(
        [text.lower() for unnamed_entity_set in unnamed_entity_sets for text in unnamed_entity_set.values()]
    )
    unnamed_entity_top = take_top_entries(unnamed_entity_count, top_n)

    # Table 4
    named_entity_types = Counter(
        [get_type(id) for named_entity_set in named_entity_sets for id in named_entity_set.keys()]
    )
    named_entity_types_top = take_top_entries(named_entity_types, top_n)

    pp({
        "dimensions": {
            "Entity count & Total": entity_set_total,
            "Entity count & Avg.": entity_set_avg,
            "Entity count & SD": entity_set_stdev,
            "Named entity count & Total": named_entity_set_total,
            "Named entity count & Avg.": named_entity_set_avg,
            "Named entity count & SD": named_entity_set_stdev,
            "Relationship triple count & Total": relationship_set_total,
            "Relationship triple count & Avg.": relationship_set_avg,
            "Relationship triple count & SD": relationship_set_stdev,
            "Synonym count & Total": synonym_set_total,
            "Synonym count & Avg.": synonym_set_avg,
            "Synonym count & SD": synonym_set_stdev
        },
        "named_entities": named_entities_top,
        "unnamed_entities": unnamed_entity_top,
        "named_entities_types": named_entity_types_top
    })


def bridge_eval(bridge_dir, top_n=20):
    visited = set()
    bridges = []
    for bridge_file in bridge_dir.glob("*.json"):
        bridge_data = read_json(bridge_file)
        for target_graph_name, bridge_map in bridge_data.items():
            key = frozenset({bridge_file.name, target_graph_name})
            if key not in visited:
                bridges.extend([[source, target] for source, target in bridge_map.items()])
                visited.add(key)

    ne_to_ne = [bridge for bridge in bridges if is_ne_ne(bridge)]
    ne_to_reg = [bridge for bridge in bridges if is_ne_re(bridge)]
    reg_to_reg = [bridge for bridge in bridges if is_re_re(bridge)]

    # Table 1
    ne_to_ne_count = len(ne_to_ne)
    ne_to_reg_count = len(ne_to_reg)
    reg_to_reg_count = len(reg_to_reg)

    # Table 2
    ne_to_ne_named_entity_count = Counter([entity for bridge in ne_to_ne for entity in bridge])
    ne_to_ne_named_entity_top = take_top_entries(ne_to_ne_named_entity_count, top_n)

    # Table 3
    ne_to_ne_named_entity_type_count = Counter([get_type(entity) for bridge in ne_to_ne for entity in bridge])
    ne_to_ne_named_entity_type_top = take_top_entries(ne_to_ne_named_entity_type_count, top_n)

    # Table 4
    ne_to_ne_same = len([bridge for bridge in ne_to_ne if bridge[0] == bridge[1]])
    ne_to_ne_same_type = len(
        [bridge for bridge in ne_to_ne if bridge[0] != bridge[1] and get_type(bridge[0]) == get_type(bridge[1])]
    )
    ne_to_ne_diff_type = len(
        [bridge for bridge in ne_to_ne if bridge[0] != bridge[1] and get_type(bridge[0]) != get_type(bridge[1])]
    )

    # Table 5
    ne_to_reg_same_text = len([bridge for bridge in ne_to_reg if get_text(bridge[0]) == get_text(bridge[1])])
    ne_to_reg_diff_text = len([bridge for bridge in ne_to_reg if get_text(bridge[0]) != get_text(bridge[1])])

    # Table 6
    ne_to_reg_contains_text = len([bridge for bridge in ne_to_reg if entity_contains_the_other(bridge)])
    ne_to_reg_does_not_contain_text = len([bridge for bridge in ne_to_reg if not entity_contains_the_other(bridge)])

    # Table 7
    ne_to_reg_named_entity_count = Counter([entity for bridge in ne_to_reg for entity in bridge if is_ne(entity)])
    ne_to_reg_named_entity_top = take_top_entries(ne_to_reg_named_entity_count, top_n)

    # Table 8
    ne_to_reg_named_entity_type_count = Counter(
        [get_type(entity) for bridge in ne_to_reg for entity in bridge if is_ne(entity)]
    )
    ne_to_reg_named_entity_type_top = take_top_entries(ne_to_reg_named_entity_type_count, top_n)

    # Table 9
    reg_to_reg_same_text = len([bridge for bridge in reg_to_reg if get_text(bridge[0]) == get_text(bridge[1])])
    reg_to_reg_diff_text = len([bridge for bridge in reg_to_reg if get_text(bridge[0]) != get_text(bridge[1])])

    # Table 10
    reg_to_reg_entity_count = Counter([get_text(entity) for bridge in reg_to_reg for entity in bridge])
    reg_to_reg_entity_top = take_top_entries(reg_to_reg_entity_count, top_n)

    # Table 11
    reg_to_reg_self_connections_count = Counter(
        [get_text(bridge[0]) for bridge in reg_to_reg if get_text(bridge[0]) == get_text(bridge[1])]
    )
    reg_to_reg_self_connections_top = {}
    for entity in reg_to_reg_entity_top:
        sc_count = reg_to_reg_self_connections_count[entity]
        sc_ratio = sc_count / (reg_to_reg_entity_top[entity] - sc_count)  # sc_count is subtracted so a self connection is not counted as two bridges  # noqa: E501
        reg_to_reg_self_connections_top[entity] = sc_count, sc_ratio

    pp({
        "count": {
            "NE-NE": ne_to_ne_count,
            "NE-RE": ne_to_reg_count,
            "RE-RE": reg_to_reg_count,
            "total": ne_to_ne_count + ne_to_reg_count + reg_to_reg_count
        },
        "NE-NE": {
            "top_entities": ne_to_ne_named_entity_top,
            "top_types": ne_to_ne_named_entity_type_top,
            "matches": {
                "same_entity": ne_to_ne_same,
                "same_type": ne_to_ne_same_type,
                "different_types": ne_to_ne_diff_type
            }
        },
        "NE-RE": {
            "same_text": {
                "match": ne_to_reg_same_text,
                "no": ne_to_reg_diff_text
            },
            "contains": {
                "match": ne_to_reg_contains_text,
                "no": ne_to_reg_does_not_contain_text
            },
            "named_entities": ne_to_reg_named_entity_top,
            "named_entity_types": ne_to_reg_named_entity_type_top
        },
        "RE-RE": {
            "same_text": {
                "match": reg_to_reg_same_text,
                "no": reg_to_reg_diff_text
            },
            "entities": reg_to_reg_entity_top,
            "self_connections": reg_to_reg_self_connections_top
        }
    })


# graph_eval(base_dir, 20)
bridge_eval(bridge_dir, 30)
