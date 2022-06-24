from .token_tree_node import TokenTreeNode

class TokenTree:
    def __init__(self, sentence):
        self.sentence = sentence
        self._setup_tree()
    
    def fetch(self, token=None, tokens=None, pool=None):
        pool = pool or self.tree
        for node in pool:
            if node.token == token or (tokens and node.token in tokens):
                return node
        if children := [child_node for node in pool for child_node in node.children]:
            return self.fetch(token, tokens, children)
        return None

    def _setup_tree(self):
        self.tree = [self._expand_node(root, "root", 0) for root in self.sentence.basicDependencies.root]

    def _expand_node(self, node_index, relation, level):
        token_edges = [edge for edge in self.sentence.basicDependencies.edge if edge.source == node_index]
        token_tree_node = TokenTreeNode(token=self.sentence.token[node_index-1], relation=relation, level=level)
        return token_tree_node.set_children([self._expand_node(edge.target, edge.dep, level+1) for edge in token_edges])