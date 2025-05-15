import shapely
import math

class Contour:
    def __init__(self, id: int, shape: shapely.LineString, contour: float):
        self.id = id
        self.shape = shape
        self.contour = contour
        self.polygon = None
        self.area = 0
        self.length = 0
        self.group = 0
        self.MMB_length = 0
        self.MMB_width = 0
        self.parent = None
        self.children = []

    def computeGeometry(self):
        self.polygon = shapely.Polygon(self.shape)
        self.area = self.polygon.area
        self.length = self.shape.length

    def testGeometry(self):
        try:
            shapely.Polygon(self.shape)
            return True
        except Exception:
            return False            
    
    def computeMMB(self):
        MMB = shapely.minimum_rotated_rectangle(self.shape)

        coords = list(MMB.exterior.coords[:-1])

        # Spočítáme délky stran (v pořadí)
        side_lengths = [math.dist(coords[i], coords[i + 1]) for i in range(len(coords) - 1)]

        # Určíme delší a kratší stranu
        self.MMB_width = min(side_lengths)
        self.MMB_length = max(side_lengths)

