import pickle
from collections import defaultdict
import math


class DGrid:

    X_scale = []
    Y_scale = []
    mapper = []
    mapperIndex = 0

    @classmethod
    def getMapperIndex(cls, point):
        i = 0
        j = 0
        for index, x in enumerate(DGrid.X_scale):
            if point[1] > x:
                i = index + 1
            else:
                break
        for index, x in enumerate(DGrid.Y_scale):
            if point[2] > x:
                j = index + 1
            else:
                break
        return i, j, j * (len(DGrid.X_scale)+1) + i

    @classmethod
    def insertPoint(cls, point, bucketSize):

        i, j, mapperIndex = DGrid.getMapperIndex(point)
        tempset = []
        with open("2d_grid/bucket" + str(DGrid.mapper[mapperIndex]) + ".txt", 'rb') as fin:
            tempset = pickle.load(fin)

        tempBuck = mapperIndex
        while len(tempset) == bucketSize+1:
            tempBuck = tempset[bucketSize]
            with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'rb') as fin:
                tempset = pickle.load(fin)

        if len(tempset) == bucketSize:
            tempset.append(DGrid.mapperIndex)
            with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'wb') as fout:
                pickle.dump(tempset, fout)
            with open("2d_grid/bucket" + str(DGrid.mapperIndex) + ".txt", 'wb') as fout:
                pickle.dump([point], fout)
                DGrid.mapperIndex += 1

        if len(tempset) < bucketSize:
            tempset.append(point)
            with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'wb') as fout:
                pickle.dump(tempset, fout)


    @classmethod
    def getKNN(cls, point, knearest, bucketSize):
        
        i, j, mapperIndex = DGrid.getMapperIndex(point)
        ktempset = []
        visitedcell = []
        visitedcellcheck = []
        bucketFetched = 0
        visitedcell.append(DGrid.mapper[mapperIndex])
        visitedcellcheck.append(mapperIndex)
        with open("2d_grid/bucket" + str(DGrid.mapper[mapperIndex]) + ".txt", 'rb') as fin:
            tempset = pickle.load(fin)
            bucketFetched += 1
            tempBuck = 0
            while len(tempset) == bucketSize+1:
                bucketFetched += 1
                for z in tempset[:-1]:
                    ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                tempBuck = tempset[bucketSize]
                with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'rb') as fin:
                    tempset = pickle.load(fin)
            for z in tempset:
                ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])

            
        min_i = i
        max_i = i
        min_j = j
        max_j = j
        while len(ktempset) < knearest:
            if min_i == 0 and max_i == len(DGrid.X_scale) and min_j == 0 and max_j == len(DGrid.Y_scale):
                print("Query Point less than required")
                break

            if min_i >= 1:
                min_i -= 1
            if max_i < len(DGrid.X_scale):
                max_i += 1
            if min_j >= 1:
                min_j -= 1
            if max_j < len(DGrid.Y_scale):
                max_j += 1
            for y in range(min_j,max_j + 1):
                for x in range(min_i,max_i + 1):
                    temp = y * (len(DGrid.X_scale)+1) + x

                    if DGrid.mapper[temp] not in visitedcell:
                        visitedcell.append(DGrid.mapper[temp])
                        visitedcellcheck.append(temp)
                        with open("2d_grid/bucket" + str(DGrid.mapper[temp]) + ".txt", 'rb') as fin:
                            tempset = pickle.load(fin)
                            bucketFetched += 1
                            tempBuck = 0
                            while len(tempset) == bucketSize+1:
                                bucketFetched += 1
                                for z in tempset[:-1]:
                                    ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                                tempBuck = tempset[bucketSize]
                                with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'rb') as fin:
                                    tempset = pickle.load(fin)
                            for z in tempset:
                                ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        if len(ktempset) > knearest:
                            break
                if len(ktempset) > knearest:
                    break
        #print("Number of bucket fetched = {}".format(len(visitedcell)))
        ktempset.sort(key=lambda x: x[3])
        #print(ktempset[knearest - 1])
        #prevvisitedcelllen = len(visitedcell)-1
        visitedNewCell = True

        while visitedNewCell:
            visitedNewCell = False

            if min_i == 0 and max_i == len(DGrid.X_scale) and min_j == 0 and max_j == len(DGrid.Y_scale):
                break

            if min_i >= 1:
                min_i -= 1
            if max_i < len(DGrid.X_scale):
                max_i += 1
            if min_j >= 1:
                min_j -= 1
            if max_j < len(DGrid.Y_scale):
                max_j += 1
            for y in range(min_j,max_j + 1):
                for x in range(min_i,max_i + 1):

                    tempx_min = -math.inf
                    tempx_max = math.inf
                    tempy_min = -math.inf
                    tempy_max = math.inf

                    try:
                        if x > 0:
                            tempx_min = DGrid.X_scale[x - 1]
                        if y > 0:
                            tempy_min = DGrid.Y_scale[y - 1]
                    except:
                        pass
                    try:
                            tempx_max = DGrid.X_scale[x]
                    except:
                            pass
                    try:
                            tempy_max = DGrid.Y_scale[y]
                    except:
                        pass
                    
                    temp = y * (len(DGrid.X_scale)+1) + x
                    
                    if x == i or y == j:
                        if y == j:
                            if tempx_max > point[1] - ktempset[knearest - 1][3] and x < i:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if DGrid.mapper[temp] not in visitedcell:
                                    visitedcell.append(DGrid.mapper[temp])
                                    with open("2d_grid/bucket" + str(DGrid.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        bucketFetched += 1
                                        tempBuck = 0
                                        while len(tempset) == bucketSize+1:
                                            bucketFetched += 1
                                            for z in tempset[:-1]:
                                                ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                                            tempBuck = tempset[bucketSize]
                                            with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'rb') as fin:
                                                tempset = pickle.load(fin)
                                        for z in tempset:
                                            ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                            if tempx_min < point[1] + ktempset[knearest - 1][3] and x > i:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if DGrid.mapper[temp] not in visitedcell:
                                    visitedcell.append(DGrid.mapper[temp])
                                    with open("2d_grid/bucket" + str(DGrid.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        bucketFetched += 1
                                        tempBuck = 0
                                        while len(tempset) == bucketSize+1:
                                            bucketFetched += 1
                                            for z in tempset[:-1]:
                                                ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                                            tempBuck = tempset[bucketSize]
                                            with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'rb') as fin:
                                                tempset = pickle.load(fin)
                                        for z in tempset:
                                            ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        if x == i:
                            if tempy_max > point[2] - ktempset[knearest - 1][3] and y < j:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if DGrid.mapper[temp] not in visitedcell:
                                    visitedcell.append(DGrid.mapper[temp])
                                    with open("2d_grid/bucket" + str(DGrid.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        bucketFetched += 1
                                        tempBuck = 0
                                        while len(tempset) == bucketSize+1:
                                            bucketFetched += 1
                                            for z in tempset[:-1]:
                                                ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                                            tempBuck = tempset[bucketSize]
                                            with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'rb') as fin:
                                                tempset = pickle.load(fin)
                                        for z in tempset:
                                            ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                            if tempy_min < point[2] + ktempset[knearest - 1][3] and y > j:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if DGrid.mapper[temp] not in visitedcell:
                                    visitedcell.append(DGrid.mapper[temp])
                                    with open("2d_grid/bucket" + str(DGrid.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        bucketFetched += 1
                                        tempBuck = 0
                                        while len(tempset) == bucketSize+1:
                                            bucketFetched += 1
                                            for z in tempset[:-1]:
                                                ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                                            tempBuck = tempset[bucketSize]
                                            with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'rb') as fin:
                                                tempset = pickle.load(fin)
                                        for z in tempset:
                                            ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        ktempset.sort(key=lambda x: x[3])

                    else:
                        if y < j and x < i :
                            if ((point[1] - tempx_max) ** 2 + (point[2] - tempy_max) ** 2) ** .5 < ktempset[knearest - 1][3]:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if DGrid.mapper[temp] not in visitedcell:
                                    visitedcell.append(DGrid.mapper[temp])
                                    with open("2d_grid/bucket" + str(DGrid.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        bucketFetched += 1
                                        tempBuck = 0
                                        while len(tempset) == bucketSize+1:
                                            bucketFetched += 1
                                            for z in tempset[:-1]:
                                                ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                                            tempBuck = tempset[bucketSize]
                                            with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'rb') as fin:
                                                tempset = pickle.load(fin)
                                        for z in tempset:
                                            ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        if y > j and x < i :
                            if ((point[1] - tempx_max) ** 2 + (point[2] - tempy_min) ** 2) ** .5 < ktempset[knearest - 1][3]:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if DGrid.mapper[temp] not in visitedcell:
                                    visitedcell.append(DGrid.mapper[temp])
                                    with open("2d_grid/bucket" + str(DGrid.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        bucketFetched += 1
                                        tempBuck = 0
                                        while len(tempset) == bucketSize+1:
                                            bucketFetched += 1
                                            for z in tempset[:-1]:
                                                ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                                            tempBuck = tempset[bucketSize]
                                            with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'rb') as fin:
                                                tempset = pickle.load(fin)
                                        for z in tempset:
                                            ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        if y > j and x > i :
                            if ((point[1] - tempx_min) ** 2 + (point[2] - tempy_min) ** 2) ** .5 < ktempset[knearest - 1][3]:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if DGrid.mapper[temp] not in visitedcell:
                                    visitedcell.append(DGrid.mapper[temp])
                                    with open("2d_grid/bucket" + str(DGrid.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        bucketFetched += 1
                                        tempBuck = 0
                                        while len(tempset) == bucketSize+1:
                                            bucketFetched += 1
                                            for z in tempset[:-1]:
                                                ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                                            tempBuck = tempset[bucketSize]
                                            with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'rb') as fin:
                                                tempset = pickle.load(fin)
                                        for z in tempset:
                                            ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        if y < j and x > i :
                            if ((point[1] - tempx_min) ** 2 + (point[2] - tempy_max) ** 2) ** .5 < ktempset[knearest - 1][3]:
                                if temp not in visitedcellcheck:
                                    visitedcellcheck.append(temp)
                                    visitedNewCell = True
                                if DGrid.mapper[temp] not in visitedcell:
                                    visitedcell.append(DGrid.mapper[temp])
                                    with open("2d_grid/bucket" + str(DGrid.mapper[temp]) + ".txt", 'rb') as fin:
                                        tempset = pickle.load(fin)
                                        bucketFetched += 1
                                        tempBuck = 0
                                        while len(tempset) == bucketSize+1:
                                            bucketFetched += 1
                                            for z in tempset[:-1]:
                                                ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                                            tempBuck = tempset[bucketSize]
                                            with open("2d_grid/bucket" + str(tempBuck) + ".txt", 'rb') as fin:
                                                tempset = pickle.load(fin)
                                        for z in tempset:
                                            ktempset.append([z[0], z[1], z[2], ((point[1] - z[1]) ** 2 + (point[2] - z[2]) ** 2) ** .5])
                        ktempset.sort(key=lambda x: x[3])
                    #print(ktempset[knearest - 1])
                    

                        


        #print("Number of bucket fetched = {}".format(len(visitedcell)))
        #print(ktempset[knearest - 1])
        return ktempset[:knearest], bucketFetched



        


bucketSize = int(input("Please enter bucket size: "))
GridSizeX = int(input("Please enter grid size x-axis: "))
GridSizeY = int(input("Please enter grid size y-axis: "))
GridCellX = int(input("Please enter grid cell x-axis: "))
GridCellY = int(input("Please enter grid cell y-axis: "))

ix = 1
while GridCellX*ix < GridSizeX:
    DGrid.X_scale.append(GridCellX*ix)
    ix += 1

ix = 1
while GridCellY*ix < GridSizeY:
    DGrid.Y_scale.append(GridCellY*ix)
    ix += 1

for x in range(0,len(DGrid.X_scale)+1):
    for y in  range(0,len(DGrid.Y_scale)+1):
        DGrid.mapper.append(DGrid.mapperIndex)
        with open("2d_grid/bucket" + str(DGrid.mapperIndex) + ".txt", 'wb') as fout:
            pickle.dump([], fout)
            DGrid.mapperIndex += 1


E = open("point32000.txt", "r")
for x in E:
    #print(x)
    temp = x.rstrip('\n').split()
    #NodeList.append([int(temp[0]), float(temp[1]), float(temp[2])])
    DGrid.insertPoint([int(temp[0]), float(temp[1]), float(temp[2])], bucketSize)

#print(DGrid.mapper)

while True:

    x = int(input("1: KNN \t 2: Print Mapper \t 3: KNN Average \t 4: Exit "))

    if x == 1:

       knearest, visitedcell = DGrid.getKNN([1, float(input("Enter X: ")), float(input("Enter Y: "))], int(input("Enter N: ")), bucketSize)
       print(knearest)
       with open("tempCheck1.txt", 'wb') as fout:
                pickle.dump(knearest, fout)
       print("Number of bucket fetched = {}".format(visitedcell))

    if x == 2:

       print(DGrid.mapper)
       for i in DGrid.mapper:
           with open("2d_grid/bucket" + str(i) + ".txt", 'rb') as fin:
               tempset = pickle.load(fin)
               print(tempset)

    
    if x == 3:
        buk = []
        bucketTemp = [5,20,50,100]
        for i in range(0,4):
            tempCount = 0
            E = open("k", "r")
            for j in E:
                temp = j.rstrip('\n').split()
                knearest, visitedcell = DGrid.getKNN([1, float(temp[0]), float(temp[1])], bucketTemp[i], bucketSize)
                tempCount = tempCount + visitedcell
            buk.append(tempCount/8)
        print(buk)

    
    if x == 4:
        break
