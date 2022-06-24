class TokenTreeNode:
    def __init__(self, token, relation="root", level=0):
        self.token = token
        self.relation = relation
        self.level = level
        self.children = []
        self.parent = None

    def set_children(self, children: list["TokenTreeNode"]):
        self.children = children
        for child in self.children:
            child.parent = self
        return self
    
    def __repr__(self) -> str:
        return f"<TokenTreeNode value=\"{self.token.value}\" {self.relation=} {self.level=} children={len(self.children)}>"