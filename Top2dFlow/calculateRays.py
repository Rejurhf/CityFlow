import numpy as np
import math as mth

# Is point in obstacle check -------------------------------------------------------------
def isPointInObstacle(point, xSize, ySize, densPerMeter, obstacles):
    for obstacle in obstacles:
        leftBorder = mth.ceil(obstacle[0] * densPerMeter)
        rightBorder = mth.floor((obstacle[0] + obstacle[1]) * densPerMeter)
        bottomBorder = mth.ceil(obstacle[2] * densPerMeter)
        topBorder = mth.floor((obstacle[2] + obstacle[3]) * densPerMeter) 

        if leftBorder <= point[0] <= rightBorder and \
                bottomBorder <= point[1] <= topBorder:
            return True
    return False


# Get shortest route ---------------------------------------------------------------------
def getShortestRoute(pointPos, xSize, ySize, densPerMeter, obstacles):
    # declare start moving point, and empty positions lists
    upPosX = pointPos[0]
    upPosY = pointPos[1] + 1
    upVisitedList = []
    downPosX = pointPos[0]
    downPosY = pointPos[1] - 1
    downVisitedList = []

    # while point not moved forward
    # try to go up
    while upPosX == pointPos[0]:
        print("Up", upPosX, upPosY)
        upVisitedList.append((upPosX, upPosY))
        if not isPointInObstacle((upPosX+1, upPosY), xSize, ySize, 
                densPerMeter, obstacles):
            upPosX += 1
        elif not isPointInObstacle((upPosX, upPosY+1), xSize, ySize, 
                densPerMeter, obstacles):
            upPosY += 1
        else:
            upPosX -= 1

    # try to go down
    while downPosX == pointPos[0]:
        print("down", downPosX, downPosY)
        downVisitedList.append((downPosX, downPosY))
        if not isPointInObstacle((downPosX+1, downPosY), xSize, ySize, 
                densPerMeter, obstacles):
            downPosX += 1
        elif not isPointInObstacle((downPosX, downPosY-1), xSize, ySize, 
                densPerMeter, obstacles):
            downPosY -= 1
        else:
            downPosX -= 1

    print("return")
    # get shorter route and return
    if len(downVisitedList) > len(upVisitedList):
        return upPosX, upPosY, upVisitedList
    else:
        return downPosX, downPosY, downVisitedList 

# Main -----------------------------------------------------------------------------------
def getFlowPathTopArrays(xSize, ySize, densPerMeter, obstacles):
    nx = int(xSize * densPerMeter) + 1 # number of points in grid
    ny = int(ySize * densPerMeter) + 1

    x = np.linspace(0,xSize,nx) # last point included, so exactly nx points
    y = np.linspace(0,ySize,ny) # last point included, so exactly ny points
    X,Y = np.meshgrid(x,y)      # makes 2-dimensional mesh grid

    v = np.zeros((ny, nx))
    u = np.zeros((ny, nx))    # for u-velocity I initialise to 1 everywhere

    
    for ray in range(ny):
        visitedPoints = []
        
        # Initial ray position
        posX = 0
        posY = ray

        while posX < nx and 0 <= posY <= ny:
            visitedPoints.append((posX, posY))

            # Determine action
            # TODO determine more actions
            if not isPointInObstacle((posX+1,posY), xSize, ySize, densPerMeter, obstacles):
                # if point x+1 is not obstacle go right
                posX += 1
            elif isPointInObstacle((posX+1, posY), xSize, ySize, densPerMeter, obstacles) and \
                    not isPointInObstacle((posX, posY + 1), xSize, ySize, densPerMeter, obstacles) and \
                    not isPointInObstacle((posX, posY - 1), xSize, ySize, densPerMeter, obstacles):
                print("getShortestRouteInit")
                posX, posY, subVisitedList = getShortestRoute((posX, posY), xSize, ySize, densPerMeter, obstacles)
                visitedPoints.extend(subVisitedList)

            elif isPointInObstacle((posX+1, posY), xSize, ySize, densPerMeter, obstacles) and \
                    not isPointInObstacle((posX, posY + 1), xSize, ySize, densPerMeter, obstacles):
                posY += 1

            elif isPointInObstacle((posX+1, posY), xSize, ySize, densPerMeter, obstacles) and \
                    not isPointInObstacle((posX, posY - 1), xSize, ySize, densPerMeter, obstacles):
                posY -= 1
            else:
                posX = nx

        # decode visitedList to flow
        if visitedPoints:
            prewPoint = (-1,-1)
            for point in visitedPoints:
                if prewPoint == (-1,-1):
                    u[point[1], point[0]] = 1
                elif point[1] > prewPoint[1]:
                    if v[point[1], point[0]] == 0:
                        v[point[1], point[0]] = 1
                    else:
                        v[point[1], point[0]] += 1
                elif point[1] < prewPoint[1]:
                    if v[point[1], point[0]] == 0:
                        v[point[1], point[0]] = -1
                    else:
                        v[point[1], point[0]] += -1
                elif point[0] > prewPoint[0]:
                    if u[point[1], point[0]] == 0:
                        u[point[1], point[0]] = 1
                    else:
                        u[point[1], point[0]] += 1
                elif point[0] < prewPoint[0]:
                    if u[point[1], point[0]] == 0:
                        u[point[1], point[0]] = -1
                    else:
                        u[point[1], point[0]] += -1
                prewPoint = point
            
    p = np.zeros((ny, nx)) # np.add(np.absolute(u), np.absolute(v))
    p = u
    # u[u == 1] = 0

    # fill array with 0 if obstacle and 1 if not
    # for i in range(ny):
    #     for j in range(nx):
    #         if isPointInObstacle((j, i), xSize, ySize, densPerMeter, obstacles):
    #             u[i,j] = 0
    #         else:
    #             u[i,j] = 1
    u[0,0] = 2.3

    return X, Y, u, v, p