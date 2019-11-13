import numpy as np

def getFlowPathSideArrays(xSize, ySize, densPerMeter, obstacles):
    nx = int(xSize * densPerMeter) + 1 # number of points in grid
    ny = int(ySize * densPerMeter) + 1

    x = np.linspace(0,xSize,nx) # last point included, so exactly nx points
    y = np.linspace(0,ySize,ny) # last point included, so exactly ny points
    X,Y = np.meshgrid(x,y)      # makes 2-dimensional mesh grid

    v = np.zeros((ny, nx))
    u = np.zeros((ny, nx))    # for u-velocity I initialise to 1 everywhere
     
    u[0,0] = 2.3

    p = np.zeros((ny, nx)) # np.add(np.absolute(u), np.absolute(v))
    p = np.add(np.absolute(u), np.absolute(v))
    # p = u
    # u[u == 1] = 0

    

    return X, Y, u, v, p