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
        downVisitedList.append((downPosX, downPosY))
        if not isPointInObstacle((downPosX+1, downPosY), xSize, ySize, 
                densPerMeter, obstacles):
            downPosX += 1
        elif not isPointInObstacle((downPosX, downPosY-1), xSize, ySize, 
                densPerMeter, obstacles):
            downPosY -= 1
        else:
            downPosX -= 1

        if downPosY < 0:
            return upPosX, upPosY, upVisitedList

    # get shorter route and return
    if len(downVisitedList) > len(upVisitedList):
        return upPosX, upPosY, upVisitedList
    else:
        return downPosX, downPosY, downVisitedList


def determineTarget(pointPos, xSize, ySize, densPerMeter, obstacles):
    nearObsIndex = 0

    # find nearest obstacle checking them one by one
    for i in range(len(obstacles)):
        if isPointInObstacle(pointPos, xSize, ySize, densPerMeter, [obstacles[i]]):
            nearObsIndex = i

    # calculate middle of obstacle y position
    nearObs = obstacles[nearObsIndex]
    target = int((nearObs[2] + (nearObs[3]/2)) * densPerMeter)
    return target


def getFlowPathSideArrays(xSize, ySize, densPerMeter, obstacles):
    nx = int(xSize * densPerMeter) + 1 # number of points in grid
    ny = int(ySize * densPerMeter) + 1

    x = np.linspace(0,xSize,nx) # last point included, so exactly nx points
    y = np.linspace(0,ySize,ny) # last point included, so exactly ny points
    X,Y = np.meshgrid(x,y)      # makes 2-dimensional mesh grid

    v = np.zeros((ny, nx))
    u = np.zeros((ny, nx))    # for u-velocity I initialise to 1 everywhere
    
    # send rays to get route
    for ray in range(ny):
        visitedPoints = []
        
        # Initial ray position
        posX = 0
        posY = ray
        targetY = -1

        while posX < nx and 0 <= posY <= ny:
            visitedPoints.append((posX, posY))

            # Determine action
            # TODO targetY zależne od tego w którym miejscu uderzony został obiekt
            if not isPointInObstacle((posX+1,posY), xSize, ySize, densPerMeter, obstacles):
                # if point x+1 is not obstacle go right
                if len(visitedPoints) > 1 and targetY >= 0 and targetY != posY and \
                        visitedPoints[-1][1] == visitedPoints[-2][1]:
                    if targetY < posY and not isPointInObstacle((posX, posY-1), 
                            xSize, ySize, densPerMeter, obstacles):
                        posY -= 1
                    elif targetY > posY and not isPointInObstacle((posX, posY+1), 
                            xSize, ySize, densPerMeter, obstacles):
                        posY += 1
                    else:
                        posX += 1
                else:
                    posX += 1
            elif isPointInObstacle((posX+1, posY), xSize, ySize, densPerMeter, obstacles) and \
                    not isPointInObstacle((posX, posY + 1), xSize, ySize, densPerMeter, 
                    obstacles) and \
                    not isPointInObstacle((posX, posY - 1), xSize, ySize, densPerMeter, 
                    obstacles):
                # get Y middle of nearest obstacle as target
                targetY = determineTarget((posX+1, posY), xSize, ySize, densPerMeter, obstacles)

                # get shortest route to move further
                posX, posY, subVisitedList = getShortestRoute((posX, posY), xSize, ySize, 
                    densPerMeter, obstacles)
                visitedPoints.extend(subVisitedList)
            elif isPointInObstacle((posX+1, posY), xSize, ySize, densPerMeter, obstacles) and \
                    not isPointInObstacle((posX, posY + 1), xSize, ySize, densPerMeter, 
                    obstacles):
                # only up path available
                posY += 1
            elif isPointInObstacle((posX+1, posY), xSize, ySize, densPerMeter, obstacles) and \
                    not isPointInObstacle((posX, posY - 1), xSize, ySize, densPerMeter, 
                    obstacles):
                # only down path available
                posY -= 1
            else:
                # no exit end program to avoid infinite loop
                posX = nx


        if visitedPoints:
            for i in range(1, len(visitedPoints)-1):
                # starting point of ray
                if i == 1:
                    u[visitedPoints[i-1][1], visitedPoints[i-1][0]] = 1

                if visitedPoints[i+1][0] == visitedPoints[i-1][0]+2:
                    # go straight right
                    u[visitedPoints[i][1], visitedPoints[i][0]] += 1
                elif visitedPoints[i+1][0] == visitedPoints[i-1][0]-2:
                    # go straight left
                    u[visitedPoints[i][1], visitedPoints[i][0]] -= 1
                elif visitedPoints[i+1][1] == visitedPoints[i-1][1]+2:
                    # go straight up
                    v[visitedPoints[i][1], visitedPoints[i][0]] += 1
                elif visitedPoints[i+1][1] == visitedPoints[i-1][1]-2:
                    # go straight down
                    v[visitedPoints[i][1], visitedPoints[i][0]] -= 1
                elif visitedPoints[i+1][0] == visitedPoints[i-1][0]+1 and \
                        visitedPoints[i+1][1] == visitedPoints[i-1][1]+1:
                    # go up right
                    u[visitedPoints[i][1], visitedPoints[i][0]] += 0.5
                    v[visitedPoints[i][1], visitedPoints[i][0]] += 0.5
                elif visitedPoints[i+1][0] == visitedPoints[i-1][0]+1 and \
                        visitedPoints[i+1][1] == visitedPoints[i-1][1]-1:
                    # go down right
                    u[visitedPoints[i][1], visitedPoints[i][0]] += 0.5
                    v[visitedPoints[i][1], visitedPoints[i][0]] += -0.5
                elif visitedPoints[i+1][0] == visitedPoints[i-1][0]-1 and \
                        visitedPoints[i+1][1] == visitedPoints[i-1][1]+1:
                    # go up left
                    u[visitedPoints[i][1], visitedPoints[i][0]] += 0.5
                    v[visitedPoints[i][1], visitedPoints[i][0]] += -0.5
                elif visitedPoints[i+1][0] == visitedPoints[i-1][0]-1 and \
                        visitedPoints[i+1][1] == visitedPoints[i-1][1]-1:
                    # go down left
                    u[visitedPoints[i][1], visitedPoints[i][0]] += -0.5
                    v[visitedPoints[i][1], visitedPoints[i][0]] += -0.5


    u[0,0] = 2.3

    p = np.zeros((ny, nx)) # np.add(np.absolute(u), np.absolute(v))
    p = np.add(np.absolute(u), np.absolute(v))
    # p = u
    # u[u == 1] = 0

    

    return X, Y, u, v, p