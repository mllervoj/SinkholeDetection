class ContourTree:
    def __init__(self, root, leaves):
        self.root = root
        self.leaves = leaves
        
        self.sortLeaves()


    def sortLeaves(self):
        self.leaves = sorted(self.leaves, key=lambda c: c.contour)