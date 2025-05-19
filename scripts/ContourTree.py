class ContourTree:
    def __init__(self, root, leaves):
        self.root = root
        self.leaves = leaves
        self.leaves = sorted(self.leaves, key=lambda c: c.height)
        