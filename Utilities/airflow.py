import numpy as np

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
    self.vX = np.zeros((self.zSize, self.ySize, self.xSize))
    self.vY = np.zeros((self.zSize, self.ySize, self.xSize))
    self.vZ = np.zeros((self.zSize, self.ySize, self.xSize))
    self.p = np.zeros((self.zSize, self.ySize, self.xSize))


  # Calculate flow -----------------------------------------------------------------------
  def calculateFlow(self):
    print("Flow calculated")


  # Get top view for specified meter above ground
  def getTopViewLayerForMeter(self, meterAboveGround):
    zLayer = int(meterAboveGround * self.densPerMeter)

    print("TODO Top view - {}m coresponds to {} z layer".format(meterAboveGround, zLayer))

  
  # Get top view for specified meter above ground
  def getSideViewLayerForMeter(self, meterFromY0):
    yLayer = int(meterFromY0 * self.densPerMeter)
    
    print("TODO Side view - {}m coresponds to {} y layer".format(meterFromY0, yLayer))