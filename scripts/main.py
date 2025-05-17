from Algorithms import Algorithms

class Main:
    def __init__(self, input_path, output_path, Parameters):        
        # Parameters
        minContourArea = Parameters[0]
        maxContourArea = Parameters[1]
        minDepth = Parameters[2]
        maxDepth = Parameters[3]
        sideCompare = Parameters[4]
        bounderySpace = 1
        minContourGroupCount = 2
        Circularity = False
        
        alg = Algorithms()
        
        #box = alg.ConvexHull(input_las)
        
        contours_all, box = alg.Contours(input_path)
        
        contours_all = alg.deleteBox(contours_all, bounderySpace, box)

        # Delete not closed contours
        newContours = []
        for contour in contours_all:
            if contour.shape.is_ring and contour.testGeometry():
                newContours.append(contour)
        contours_all = newContours
        
        
        
        # Compute contour geometry
        for contour in contours_all:
            contour.computeGeometry()
        
        if minContourArea != False:
            contours = [item for item in contours_all if item.area > minContourArea]
        else:
            contours = contours_all        
        
        # Compute groups of contours
        contours = alg.groupContours(contours)
        
        # Deletig group with less than 4 mambers
        groups, contours = alg.deleteSmallGroups(contours, minContourGroupCount)
        
        finalContour = []
        for group in groups:
            groupContour = [item for item in contours if item.group == group]
        
            groupContour, tree = alg.createTree(groupContour)
        
            finalContour = alg.MaxContour(tree, finalContour, maxContourArea)
         
        uniqeContour = alg.UniqeContour(finalContour)
        
        conture_filtrated = alg.filtration(uniqeContour, contours_all, minContourArea, maxContourArea, sideCompare, minDepth, maxDepth, Circularity)
        
        alg.createShp(conture_filtrated, output_path)
        