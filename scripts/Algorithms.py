from collections import Counter
import shapely
import geopandas as gpd
import math

from Contour import Contour
from ContourTree import ContourTree

class Algorithms:

    def __init__(self):
        pass
        
    def Contours(self, input):
        gdf = gpd.read_file(input)
        id = 1
        contours = []
        for index, row in gdf.iterrows():
            contours.append(Contour(id, row['geometry'], round(row['Contour'],1)))
            id += 1
            
        union_geom = gdf.geometry.unary_union
        minx, miny, maxx, maxy = union_geom.bounds
        bounding_box = shapely.LineString([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)])
            
        return contours, bounding_box
    
    def deleteBox(self, con, space, box):
        buffered_box = box.buffer(space)
        
        contour = [item for item in con if not item.shape.intersects(buffered_box)]
        
        return contour
        
    def groupContours(self, con):

        conSorted = sorted(con, key=lambda c: c.area, reverse=True)

        group = 1
        while conSorted:
            filteredContours = [item.id for item in conSorted if conSorted[0].polygon.contains(item.polygon)]

            if filteredContours:
                conSorted = [item for item in conSorted if item.id not in filteredContours]

            for contour in con:
                if contour.id in filteredContours:
                    contour.group = group

            group += 1

        return con

    def deleteSmallGroups(self, con, group_count):
        group_counts = Counter(c.group for c in con)
        filtered_contours = [c for c in con if group_counts[c.group] >= group_count]

        groups = [c.group for c in filtered_contours]

        unique_groups = list(set(groups))

        return unique_groups, filtered_contours

    def Brench(self, min, con):
        branche = [item for item in con if item.polygon.contains(min.polygon)]

        brancheIds = [item.id for item in branche]

        con = [item for item in con if item.id not in brancheIds]

        return branche, con

    def MinContain(self, max, con):

        cont = [item for item in con if item.polygon.contains(max.polygon)]

        cont_delete = [item for item in cont if item.id != max.id]

        cont_min = min(cont_delete, key=lambda c: c.area)

        return cont_min

    def Tree(self, con):
        start = True
        conAll = con
        while con:
            minContour = min(con, key=lambda c: c.area)

            branche, con = self.Brench(minContour, con)

            brancheSorted = sorted(branche, key=lambda c: c.area, reverse=True)

            first = True

            for contour in brancheSorted:
                if first:
                    first = False
                    contourBefore = contour
                    if not start:
                        minCon = self.MinContain(contour, conAll)
                        for contour_change in conAll:
                            if contour_change.id == minCon.id:
                                contour_change.children.append(contour)
                            if contour_change.id == contour.id:
                                contour_change.parent = minCon

                else:
                    for contour_change in conAll:
                        if contour_change.id == contourBefore.id:
                            contour_change.children.append(contour)
                        if contour_change.id == contour.id:
                            contour_change.parent = contourBefore

                    contourBefore = contour

            if start:
                start = False

        root = None
        leaves = []
        for cont in conAll:
            if cont.parent is None:
                root = cont
            if not cont.children:
                leaves.append(cont)
        
        tree = ContourTree(root, leaves)
        
        return conAll, tree

    def MaxContour(self, tree, finalContour, maxArea):
        
        if maxArea is False:
            maxArea = math.inf
        
        for leaf in tree.leaves:
            leafHeight = leaf.contour
            maxHeight = leafHeight
            maxContour = leaf
            contourBefore = leaf
            Continue = True
            while Continue:
                contourNow = contourBefore.parent
                
                if contourNow.area > maxArea:
                    Continue = False

                if Continue is True:
                    if maxHeight < contourNow.contour:
                        maxHeight = contourNow.contour
                        maxContour = contourNow
                    contourBefore = contourNow
                    
                if contourNow.parent is None:
                    Continue = False


            if maxHeight > leafHeight:
                finalContour.append(maxContour)

        return finalContour

    def UniqeContour(self, con):
        con = self.groupContours(con)

        best_contours = {}

        for contour in con:
            if contour.group not in best_contours or contour.area > best_contours[contour.group].area:
                best_contours[contour.group] = contour

        result_list = list(best_contours.values())

        return result_list

    def filtration(self, con, con_all, min_area, max_area, side_compare, min_depth, max_depth, Circularity):

        # Contour mast be biger then parameter
        if min_area != False:
            con = [item for item in con if item.area >= min_area]

        # Contour mast be smaller then parameter
        if max_area != False:
            con = [item for item in con if item.area <= max_area]

        for contour in con:
            contour.computeMMB()

        # Contour cant be to long
        if side_compare != False:
            con = [item for item in con if side_compare*item.MMB_width > item.MMB_length]

        # Depth inside contour mast be more then parameter
        if min_depth != False:
            con_new = []
            for contour in con:
                con_contain = [item.contour for item in con_all if contour.polygon.contains(item.polygon)]
                if min(con_contain) + min_depth/100 <= max(con_contain):
                    con_new.append(contour)
            con = con_new
        
        # Depth inside contour mast be less then parameter
        if max_depth != False:
            con_new = []
            for contour in con:
                con_contain = [item.contour for item in con_all if contour.polygon.contains(item.polygon)]
                if min(con_contain) + max_depth/100 >= max(con_contain):
                    con_new.append(contour)
            con = con_new
        
        # Pořešit jestli nějak zapojovat
        #con = [item for item in con if ((4*math.pi*item.area)/(item.area**2)) > Circularity]

        return con
    
    def createShp(self, con, path):
        geometries = [contour.polygon for contour in con]
        
        gdf = gpd.GeoDataFrame(geometry=geometries)
        
        gdf.set_crs("EPSG:5514", allow_override=True, inplace=True)
        
        gdf.to_file(path)