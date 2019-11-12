import numpy as np
import math as mth

def getObstacleBorders(u, xSize, ySize, obstacle, rounded=True):
    xMul = (len(u[0]) - 1) / (xSize)
    yMul = (len(u) - 1) / (ySize)

    if rounded:
        left = mth.ceil(obstacle[0] * xMul)
        right = mth.floor((obstacle[0] + obstacle[1]) * xMul)
        bottom = mth.ceil(obstacle[2] * yMul)
        top = mth.floor((obstacle[2] + obstacle[3]) * yMul)
    else:
        left = obstacle[0] * xMul
        right = (obstacle[0] + obstacle[1]) * xMul
        bottom = obstacle[2] * yMul
        top = (obstacle[2] + obstacle[3]) * yMul

    return left, right, bottom, top


# Is point in obstacle check ---------------------------------------------------
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


# Main -------------------------------------------------------------------------
def getFlowPathTopArrays(xSize, ySize, densPerMeter, obstacles):
    nx = int(xSize * densPerMeter) + 1 # number of points in grid
    ny = int(ySize * densPerMeter) + 1

    x = np.linspace(0,xSize,nx) # last point included, so exactly nx points
    y = np.linspace(0,ySize,ny) # last point included, so exactly ny points
    X,Y = np.meshgrid(x,y)      # makes 2-dimensional mesh grid

    v = np.zeros((ny, nx))
    u = np.zeros((ny, nx))    # for u-velocity I initialise to 1 everywhere

    p = np.zeros((ny, nx)) # np.add(np.absolute(u), np.absolute(v))
    p = u
    # u[u == 1] = 0

    # fill array with 0 if obstacle and 1 if not
    for i in range(ny):
        for j in range(nx):
            if isPointInObstacle((j, i), xSize, ySize, densPerMeter, obstacles):
                u[i,j] = 0
            else:
                u[i,j] = 1
    u[0,0] = 2.3

    return X, Y, u, v, p