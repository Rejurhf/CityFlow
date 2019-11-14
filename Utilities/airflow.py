import numpy as np
from Utilities import visualize, rays2dcalculator


class AirFlow:
  def __init__(self, xSize, ySize, zSize, densPerMeter, obstacleList):
    self.xSize = xSize
    self.ySize = ySize
    self.zSize = zSize
    self.densPerMeter = densPerMeter
    self.obstacleList = obstacleList
    
    # Calculate points in every axis
    nx = int(self.xSize * self.densPerMeter) + 1 # number of points in grid
    ny = int(self.ySize * self.densPerMeter) + 1
    nz = int(self.zSize * self.densPerMeter) + 1

    # Create 3d arrays
    self.vX = np.zeros((nz, ny, nx))
    self.vY = np.zeros((nz, ny, nx))
    self.vZ = np.zeros((nz, ny, nx))
    self.p = np.zeros((nz, ny, nx))

  # Convert 3d obstacles to 2d
  def convertObstaclesTo2d(self, isTopView = True):
    obstacleList2d = []
    if isTopView:
      for obstacle in self.obstacleList:
        obstacleList2d.append([obstacle[0], obstacle[1], obstacle[2], obstacle[3]])
    else:
      for obstacle in self.obstacleList:
        obstacleList2d.append([obstacle[0], obstacle[1], obstacle[4], obstacle[5]])
    
    return obstacleList2d


  # Get side view from 3d array
  def getSideView2dArray(self, array3d, yLayer):
    # Calculate points in every axis
    nx = int(self.xSize * self.densPerMeter) + 1 # number of points in grid
    nz = int(self.zSize * self.densPerMeter) + 1

    # Declare empty array to return
    array2d = np.empty([nz, nx])

    # Convert 3d array to 2d
    for i in range(nz):
      for j in range(nx):
        array2d[i,j] = array3d[i, yLayer, j]
      
    return array2d


  # Calculate flow -----------------------------------------------------------------------
  def calculateFlow(self):
    print("AF:", "Flow calculated")


  # Get top view for specified meter above ground ----------------------------------------
  def getTopViewLayerForMeter(self, meterAboveGround):
    # Calculate layer coresponding to given meter
    zLayer = int(meterAboveGround * self.densPerMeter)

    # Calculate values for plot
    nx = int(self.xSize * self.densPerMeter) + 1 # number of points in grid
    ny = int(self.ySize * self.densPerMeter) + 1

    x = np.linspace(0, self.xSize, nx) # last point included, so exactly nx points
    y = np.linspace(0, self.ySize, ny) # last point included, so exactly ny points
    
    X,Y = np.meshgrid(x, y)     # makes 2-dimensional mesh grid
    array2dX = self.vX[zLayer]  # Get layers
    array2dY = self.vY[zLayer]
    array2dP = self.p[zLayer]
    listOf2dObstacles = self.convertObstaclesTo2d(isTopView = True)

    # Print text and display plot
    titleText = "{}m above ground ({} Z axis layer)".format(meterAboveGround, zLayer+1)
    print("AF:", titleText)
    visualize.showPlot(X, Y, array2dX, array2dY, array2dP, listOf2dObstacles, titleText)

  
  # Get side view for specified meter above ground --------------------------------------- 
  def getSideViewLayerForMeter(self, meterFromY0):
    # Calculate layer coresponding to given meter
    yLayer = int(meterFromY0 * self.densPerMeter)

    # Calculate values for plot
    nx = int(self.xSize * self.densPerMeter) + 1 # number of points in grid
    nz = int(self.zSize * self.densPerMeter) + 1

    x = np.linspace(0, self.xSize, nx) # last point included, so exactly nx points
    z = np.linspace(0, self.zSize, nz) # last point included, so exactly ny points
    
    X,Z = np.meshgrid(x, z)     # makes 2-dimensional mesh grid
    array2dX = self.getSideView2dArray(self.vX, yLayer) # Get layers
    array2dZ = self.getSideView2dArray(self.vZ, yLayer)
    array2dP = self.getSideView2dArray(self.p, yLayer)
    listOf2dObstacles = self.convertObstaclesTo2d(isTopView = False)
    
    # Print text and display plot
    titleText = "{}m from left ({} Y axis layer)".format(meterFromY0, yLayer+1)
    print("AF:", titleText)
    visualize.showPlot(X, Z, array2dX, array2dZ, array2dP, listOf2dObstacles, titleText)