from manimlib import *


class BaumUmdrehe(Scene):
    def construct(self):

        tree = input()

        def createNodeCounts():
            nodeCounts = []
            maxDepth = 0
            depth = -1
            oldLines = []
            index = 0
            while index < len(tree):
                if tree[index] == '(':
                    depth += 1
                    if len(oldLines) <= depth:  # da wir am Anfang nicht wissen, wie tief wir gehen
                        oldLines.append(False)
                        nodeCounts.append([])
                    if oldLines[depth]:
                        nodeCounts[depth][-1] += 1  # +1 zu den childs
                    else:
                        oldLines[depth] = True
                        nodeCounts[depth].append(1)  # append und nicht +1

                    if tree[index + 1] == ')':
                        if maxDepth != depth:
                            if maxDepth == 0:  # höhe überprüfe
                                maxDepth = depth
                            else:
                                return False
                        depth -= 1
                        index += 1  # überspringe )
                else:  # ))
                    oldLines[depth + 1] = False
                    depth -= 1
                index += 1
            return nodeCounts

        def calcNodesWidth(index, depth, multiplier):
            widths = []
            if depth + 1 < maxDepth:
                sume = 0
                for i in range(index):
                    sume += nodes[depth][i]
                for i in range(nodes[depth][index]):
                    widths.extend(calcNodesWidth(sume + i, depth + 1, multiplier * nodes[depth][index]))
                return widths
            else:
                for i in range(nodes[depth][index]):
                    widths.append(multiplier * nodes[depth][index])
                return widths

        def findMiddle():
            depth = 2
            noMiddle = nodes[depth - 1][0] % 2 == 0
            middle = (nodes[depth - 1][0] - 1) // 2

            while depth < maxDepth:
                summe = 0
                for i in range(middle):
                    summe += nodes[depth][i]

                if not noMiddle and nodes[depth][middle] % 2 == 0:
                    noMiddle = True
                    middle = summe + (nodes[depth][middle] - 1) // 2
                else:
                    if not noMiddle:
                        middle = summe + (nodes[depth][middle] - 1) // 2
                    else:
                        middle = summe + nodes[depth][middle] - 1
                depth += 1

            return middle, noMiddle

        def evalRotation():
            widths = calcNodesWidth(0, 0, 1)
            middle = findMiddle()
            if len(widths[:middle[0] + 1 if middle[1] else middle[0]]) != len(
                    widths[middle[0] + 1:]):  # mitte in der mitte?
                return False

            for i in range(middle[0] + 1 if middle[1] else middle[0]):  # vergleiche gegenseitige Fläche
                if widths[i] != widths[-i - 1]:
                    return False
            return True


        def calcAmountOfChildren(currIndex):
            depth = 0
            summe = 0
            while currIndex < len(tree) and depth != -1:
                if tree[currIndex] == '(':
                    depth += 1
                else:
                    depth -= 1
                if depth == 0:
                    summe += 1
                currIndex += 1
            return summe

        screenWidth = 6
        screenHeight = 6

        def createKnots(parent, parentRec, currIndex, depth):
            currRelativeIndex = 1

            childrenAmount = calcAmountOfChildren(currIndex)

            circles = []
            labels = []
            lines = []
            recs = []
            while currIndex < len(tree):
                if tree[currIndex] == '(':
                    recRadius = parentRec.get_width() / childrenAmount
                    rec = Rectangle(height=screenHeight/maxDepth, width=recRadius).move_to(parentRec.get_corner(DL) + DOWN * (screenHeight/maxDepth / 2) + RIGHT * ((currRelativeIndex - 1) * recRadius + recRadius / 2))
                    circle = Circle(radius=min(rec.get_height(), rec.get_width()) / 2).move_to(rec.get_center())
                    label = Text(str(currIndex), font_size=8).move_to(circle.get_center())
                    circles.append(circle)
                    labels.append(label)
                    lines.append(Line(parent.get_bottom(), circle.get_top()))
                    recs.append(rec)

                    currRelativeIndex += 1
                    currIndex += 1
                    if tree[currIndex] == '(':
                        temp = createKnots(circle, rec, currIndex, depth + 1)
                        circles.extend(temp[0])
                        labels.extend(temp[1])
                        lines.extend(temp[2])
                        recs.extend(temp[3])
                        currIndex = temp[4]
                        if currIndex >= len(tree):
                            return circles, labels, lines, recs, currIndex
                if tree[currIndex] == ')':
                    if tree[currIndex - 1] == ')':
                        return circles, labels, lines, recs, currIndex + 1
                    currIndex += 1
                    if currIndex >= len(tree):
                        return circles, labels, lines, recs, currIndex
                if tree[currIndex] == ')':
                    return circles, labels, lines, recs, currIndex + 1

            return circles, labels, lines, recs, currIndex

        def playAnimation():
            rec = Rectangle(height=screenHeight/maxDepth, width=screenWidth).move_to(self.camera.frame.get_top())
            root = Circle(radius=min(rec.get_height(), rec.get_width()) / 2).move_to(rec.get_center())
            root_label = Text("A").move_to(root.get_center())
            if tree != '()':
                collectionToBeDrawn = createKnots(root, rec, 1, 1)
            else:
                collectionToBeDrawn = [[], [], [], []]
            collectionToBeDrawn = (
            [root, *collectionToBeDrawn[0]], [root_label, *collectionToBeDrawn[1]], collectionToBeDrawn[2], [rec, *collectionToBeDrawn[3]],)
            treeG = VGroup(*(collectionToBeDrawn[0]), *(collectionToBeDrawn[1]), *(collectionToBeDrawn[2]), *(collectionToBeDrawn[3]))
            rotatingTree = treeG.copy()
            rotatingSquares = VGroup(*(collectionToBeDrawn[3]).copy())
            self.play(ShowCreation(VGroup(*(collectionToBeDrawn[0]))), run_time=2)
            self.play(LaggedStartMap(FadeIn, VGroup(*(collectionToBeDrawn[1])), shift=0.2 * UP))
            self.play(Write(VGroup(*(collectionToBeDrawn[2]))))
            self.play(Write(VGroup(*(collectionToBeDrawn[3]))))
            self.wait(0.5)
            self.play(Rotate(rotatingTree, PI, about_point=treeG.get_bottom()), run_time=3)

        nodes = createNodeCounts()
        if nodes:
            maxDepth = len(nodes)
            print("Antwort ist: " + str(evalRotation()) + " die Flächen sind: " + str(calcNodesWidth(0, 0, 1)) + " die Mitte ist: " + str(findMiddle()))
            print("neue Darstellung war: " + str(nodes))
            playAnimation()
        else:
            print('False wegen Höhe')
            input("press enter to exit")
