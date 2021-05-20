import pickle
from collections import defaultdict
import math


class GridFiles:

    X_scale = []
    Y_scale = []
    mapper = []
    xscalelen = 1
    yscalelen = 1
    splitAxis = 'x'
    mapperIndex = 0

    @classmethod
    def getMapperIndex(cls, point):
        i = 0
        j = 0
        for index, x in enumerate(GridFiles.X_scale):
            if point[1] > x:
                i = index + 1
            else:
                break
        for index, x in enumerate(GridFiles.Y_scale):
            if point[2] > x:
                j = index + 1
            else:
                break
        return i, j, j * GridFiles.xscalelen + i


    @classmethod
    def getMedian(cls, pointSet, bucketSize):
        splitLeft = []
        splitRight = []
        if GridFiles.splitAxis == 'x':
            pointSet.sort(key=lambda x: x[1])
            splitMedian = (pointSet[int(bucketSize / 2) - 1][1] + pointSet[int(bucketSize / 2)][1]) / 2
            for x in pointSet:
                if x[1] <= splitMedian:
                    splitLeft.append(x)
                else:
                    splitRight.append(x)
            if len(splitLeft) == bucketSize or len(splitRight) == bucketSize:
                GridFiles.splitAxis = 'y'
                return GridFiles.getMedian(pointSet, bucketSize)
            return splitLeft, splitRight, splitMedian
        else:
            pointSet.sort(key=lambda x: x[2])
            splitMedian = (pointSet[int(bucketSize / 2) - 1][2] + pointSet[int(bucketSize / 2)][2]) / 2
            for x in pointSet:
                if x[2] <= splitMedian:
                    splitLeft.append(x)
                else:
                    splitRight.append(x)
            if len(splitLeft) == bucketSize or len(splitRight) == bucketSize:
                GridFiles.splitAxis = 'x'
                return GridFiles.getMedian(pointSet, bucketSize)
            return splitLeft, splitRight, splitMedian


    @classmethod
    def checkLimit(cls, i, j, pointSet, bucketSize):
        try:
            x_min = -math.inf
            x_max = math.inf
            y_min = -math.inf
            y_max = math.inf

            try:
                if i > 0:
                    x_min = GridFiles.X_scale[i - 1]
                if j > 0:
                    y_min = GridFiles.Y_scale[j - 1]
            except:
                pass
            try:
                x_max = GridFiles.X_scale[i]
            except:
                pass
            try:
                y_max = GridFiles.Y_scale[j]
            except:
                pass
            
            num = 0
            for x in pointSet:
                if x_min <= x[1] and x_max >= x[1] and y_min <= x[2] and y_max >= x[2]:
                    num += 1

            if bucketSize > num:
                return True
            return False
        except:
            return False


    @classmethod
    def checkPointSet(cls, i, j, pointSet, bucketSize):
        
        x_min = -math.inf
        x_max = math.inf
        y_min = -math.inf
        y_max = math.inf

        try:
            if i > 0:
                x_min = GridFiles.X_scale[i - 1]
            if j > 0:
                y_min = GridFiles.Y_scale[j - 1]
        except:
            pass
        try:
            x_max = GridFiles.X_scale[i]
        except:
            pass
        try:
            y_max = GridFiles.Y_scale[j]
        except:
            pass

        splitLeft = []
        splitRight = []
        for x in pointSet:
            if x_min <= x[1] and x_max >= x[1] and y_min <= x[2] and y_max >= x[2]:
                splitLeft.append(x)
            else:
                splitRight.append(x)

        return splitLeft, splitRight


    @classmethod
    def insertPoint(cls, point, bucketSize):

        i, j, mapperIndex = GridFiles.getMapperIndex(point)
        pointSet = []
        with open("grid_file/bucket" + str(GridFiles.mapper[mapperIndex]) + ".txt", 'rb') as fin:
            pointSet = pickle.load(fin)

        if len(pointSet) < bucketSize:
            pointSet.append(point)
            with open("grid_file/bucket" + str(GridFiles.mapper[mapperIndex]) + ".txt", 'wb') as fout:
                pickle.dump(pointSet, fout)

        elif GridFiles.checkLimit(i, j, pointSet, bucketSize) == True:
            pointSet.append(point)
            splitLeft, splitRight = GridFiles.checkPointSet(i, j, pointSet, bucketSize)
            with open("grid_file/bucket" + str(GridFiles.mapper[mapperIndex]) + ".txt", 'wb') as fout:
                pickle.dump(splitRight, fout)
            with open("grid_file/bucket" + str(GridFiles.mapperIndex) + ".txt", 'wb') as fout:
                pickle.dump(splitLeft, fout)
            GridFiles.mapper[mapperIndex] = GridFiles.mapperIndex
            GridFiles.mapperIndex += 1

        else:
            pointSet.append(point)
            splitLeft, splitRight, splitMedian = GridFiles.getMedian(pointSet, bucketSize)
            bucketToEmpty = GridFiles.mapper[mapperIndex]
            if GridFiles.splitAxis == 'x':
                tempMapperList = defaultdict(list)
                for y in range(GridFiles.yscalelen):
                    temp = y * GridFiles.xscalelen + i
                    if y == j:
                        with open("grid_file/bucket" + str(GridFiles.mapperIndex) + ".txt", 'wb') as fout:
                            pickle.dump(splitLeft, fout)
                        tempMapperList[temp].append(GridFiles.mapperIndex)
                        GridFiles.mapperIndex += 1
                        with open("grid_file/bucket" + str(GridFiles.mapperIndex) + ".txt", 'wb') as fout:
                            pickle.dump(splitRight, fout)
                        tempMapperList[temp].append(GridFiles.mapperIndex)
                        GridFiles.mapperIndex += 1
                    else:
                        tempMapperList[temp].append(GridFiles.mapper[temp])
                        tempMapperList[temp].append(GridFiles.mapper[temp])

                temp = 0
                for key in sorted(tempMapperList):
                    GridFiles.mapper.pop(key + temp)
                    temp2 = 0
                    for x in tempMapperList[key]:
                        GridFiles.mapper.insert(key + temp + temp2, x)
                        temp2 += 1
                    temp += 1
                with open("grid_file/bucket" + str(bucketToEmpty) + ".txt", 'wb') as fout:
                    pickle.dump([], fout)
                GridFiles.splitAxis = 'y'
                GridFiles.X_scale.append(splitMedian)
                GridFiles.X_scale.sort()
                GridFiles.xscalelen += 1

            else:
                tempMapperList = defaultdict(list)
                for x in range(GridFiles.xscalelen):
                    temp = j * GridFiles.xscalelen + x
                    if x == i:
                        with open("grid_file/bucket" + str(GridFiles.mapperIndex) + ".txt", 'wb') as fout:
                            pickle.dump(splitLeft, fout)
                        tempMapperList[temp].append(GridFiles.mapperIndex)
                        GridFiles.mapperIndex += 1
                        with open("grid_file/bucket" + str(GridFiles.mapperIndex) + ".txt", 'wb') as fout:
                            pickle.dump(splitRight, fout)
                        tempMapperList[temp].append(GridFiles.mapperIndex)
                        GridFiles.mapperIndex += 1
                    else:
                        tempMapperList[temp].append(GridFiles.mapper[temp])
                        tempMapperList[temp].append(GridFiles.mapper[temp])
                temp = 0
                for key in sorted(tempMapperList):
                    GridFiles.mapper.pop(key + temp)
                    for x in tempMapperList[key]:
                        GridFiles.mapper.insert(key + temp, x)
                        temp = GridFiles.xscalelen
                    temp = 0
                with open("grid_file/bucket" + str(bucketToEmpty) + ".txt", 'wb') as fout:
                    pickle.dump([], fout)
                GridFiles.splitAxis = 'x'
                GridFiles.Y_scale.append(splitMedian)
                GridFiles.Y_scale.sort()
                GridFiles.yscalelen += 1



    @classmethod
    def getKNN(cls, point, knearest):
        
        i, j, mapperIndex = GridFiles.getMapperIndex(point)
        kpointSet = []
        visitedcell = []
        visitedcellcheck = []
        visitedcell.append(GridFiles.mapper[mapperIndex])
        visitedcellcheck.append(mapperIndex)
        with open("grid_file/bucket" + str(GridFiles.mapper[mapperIndex]) + ".txt", 'rb') as fin:
            tempset = pickle.load(fin)
            for z in tempset:
                kpointSet.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])

            
        min_i = i
        max_i = i
        min_j = j
        max_j = j
        while len(kpointSet) < knearest:
            if min_i == 0 and max_i == GridFiles.xscalelen - 1 and min_j == 0 and max_j == GridFiles.yscalelen - 1:
                print("Query Point less than required")
                break
            if min_i >= 1:
                min_i -= 1
            if max_i < GridFiles.xscalelen - 1:
                max_i += 1
            if min_j >= 1:
                min_j -= 1
            if max_j < GridFiles.yscalelen - 1:
                max_j += 1
            for y in range(min_j,max_j + 1):
                for x in range(min_i,max_i + 1):
                    temp = y * GridFiles.xscalelen + x
                    if GridFiles.mapper[temp] not in visitedcell:
                        visitedcell.append(GridFiles.mapper[temp])
                        visitedcellcheck.append(temp)
                        with open("grid_file/bucket" + str(GridFiles.mapper[temp]) + ".txt", 'rb') as fin:
                            tempset = pickle.load(fin)
                            for z in tempset:
                                kpointSet.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        if len(kpointSet) > knearest:
                            break
                if len(kpointSet) > knearest:
                    break
        #print("Number of bucket fetched = {}".format(len(visitedcell)))
        kpointSet.sort(key=lambda x: x[3])
        #print(kpointSet[knearest - 1])
        #prevvisitedcelllen = len(visitedcell)-1
        visitedNewCell = True

        while visitedNewCell:
            visitedNewCell = False

            if min_i == 0 and max_i == GridFiles.xscalelen - 1 and min_j == 0 and max_j == GridFiles.yscalelen - 1:
                break

            if min_i >= 1:
                min_i -= 1
            if max_i < GridFiles.xscalelen - 1:
                max_i += 1
            if min_j >= 1:
                min_j -= 1
            if max_j < GridFiles.yscalelen - 1:
                max_j += 1
            for y in range(min_j,max_j + 1):
                for x in range(min_i,max_i + 1):

                    tempx_min = -math.inf
                    tempx_max = math.inf
                    tempy_min = -math.inf
                    tempy_max = math.inf

                    try:
                        if x > 0:
                            tempx_min = GridFiles.X_scale[x - 1]
                        if y > 0:
                            tempy_min = GridFiles.Y_scale[y - 1]
                    except:
                        pass
                    try:
                            tempx_max = GridFiles.X_scale[x]
                    except:
                            pass
                    try:
                            tempy_max = GridFiles.Y_scale[y]
                    except:
                        pass
                    
                    temp = y * GridFiles.xscalelen + x
                    
                    if x == i or y == j:
                        if y == j:
                            if tempx_max >= point[1] - kpointSet[knearest - 1][3] and x < i:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if GridFiles.mapper[temp] not in visitedcell:
                                    visitedcell.append(GridFiles.mapper[temp])
                                    with open("grid_file/bucket" + str(GridFiles.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        for z in tempset:
                                            kpointSet.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                            if tempx_min < point[1] + kpointSet[knearest - 1][3] and x > i:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if GridFiles.mapper[temp] not in visitedcell:
                                    visitedcell.append(GridFiles.mapper[temp])
                                    with open("grid_file/bucket" + str(GridFiles.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        for z in tempset:
                                            kpointSet.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        if x == i:
                            if tempy_max > point[2] - kpointSet[knearest - 1][3] and y < j:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if GridFiles.mapper[temp] not in visitedcell:
                                    visitedcell.append(GridFiles.mapper[temp])
                                    with open("grid_file/bucket" + str(GridFiles.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        for z in tempset:
                                            kpointSet.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                            if tempy_min <= point[2] + kpointSet[knearest - 1][3] and y > j:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if GridFiles.mapper[temp] not in visitedcell:
                                    visitedcell.append(GridFiles.mapper[temp])
                                    with open("grid_file/bucket" + str(GridFiles.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        for z in tempset:
                                            kpointSet.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        kpointSet.sort(key=lambda x: x[3])

                    else:
                        if y < j and x < i :
                            if ((point[1] - tempx_max) ** 2 + (point[2] - tempy_max) ** 2) ** .5 < kpointSet[knearest - 1][3]:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if GridFiles.mapper[temp] not in visitedcell:
                                    visitedcell.append(GridFiles.mapper[temp])
                                    with open("grid_file/bucket" + str(GridFiles.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        for z in tempset:
                                            kpointSet.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        if y > j and x < i :
                            if ((point[1] - tempx_max) ** 2 + (point[2] - tempy_min) ** 2) ** .5 < kpointSet[knearest - 1][3]:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if GridFiles.mapper[temp] not in visitedcell:
                                    visitedcell.append(GridFiles.mapper[temp])
                                    with open("grid_file/bucket" + str(GridFiles.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        for z in tempset:
                                            kpointSet.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        if y > j and x > i :
                            if ((point[1] - tempx_min) ** 2 + (point[2] - tempy_min) ** 2) ** .5 < kpointSet[knearest - 1][3]:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if GridFiles.mapper[temp] not in visitedcell:
                                    visitedcell.append(GridFiles.mapper[temp])
                                    with open("grid_file/bucket" + str(GridFiles.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        for z in tempset:
                                            kpointSet.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        if y < j and x > i :
                            if ((point[1] - tempx_min) ** 2 + (point[2] - tempy_max) ** 2) ** .5 < kpointSet[knearest - 1][3]:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if GridFiles.mapper[temp] not in visitedcell:
                                    visitedcell.append(GridFiles.mapper[temp])
                                    with open("grid_file/bucket" + str(GridFiles.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        for z in tempset:
                                            kpointSet.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        kpointSet.sort(key=lambda x: x[3])
                    #print(kpointSet[knearest - 1])
                    

                        


        #print("Number of bucket fetched = {}".format(len(visitedcell)))
        #print(kpointSet[knearest - 1])
        return kpointSet[:knearest], visitedcell

        


bucketSize = int(input("Please enter bucket size: "))
tmp = []
GridFiles.mapper.append(GridFiles.mapperIndex)
with open("grid_file/bucket" + str(GridFiles.mapperIndex) + ".txt", 'wb') as fout:
    pickle.dump([], fout)
    GridFiles.mapperIndex += 1

E = open("point32000.txt", "r")
for x in E:
    #print(x)
    temp = x.rstrip('\n').split()
    #NodeList.append([int(temp[0]), float(temp[1]), float(temp[2])])
    GridFiles.insertPoint([int(temp[0]), float(temp[1]), float(temp[2])], bucketSize)

#print(GridFiles.mapper)

while True:

    x = int(input("1: KNN \t 2: Print Mapper \t 3: KNN Average \t 4: Exit "))

    if x == 1:

       knearest, visitedcell = GridFiles.getKNN([1, float(input("Enter X: ")), float(input("Enter Y: "))], int(input("Enter N: ")))
       print(knearest)
       with open("tempCheck1.txt", 'wb') as fout:
                pickle.dump(knearest, fout)
       print("Number of bucket fetched = {}".format(len(visitedcell)))

    if x == 2:

       print(GridFiles.mapper)
    
    if x == 3:
        buk = []
        bucketTemp = [5,20,50,100]
        for i in range(0,4):
            tempCount = 0
            E = open("k", "r")
            for j in E:
                temp = j.rstrip('\n').split()
                knearest, visitedcell = GridFiles.getKNN([1, float(temp[0]), float(temp[1])], bucketTemp[i])
                tempCount = tempCount + len(visitedcell)
            buk.append(tempCount/8)
        print(buk)

    
    if x == 4:
        break
