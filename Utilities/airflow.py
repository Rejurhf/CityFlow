import numpy as np
from utilities import visualize, rays2dcalculator


class AirFlow:
  def __init__(self, xSize, ySize, zSize, densPerMeter, obstacleList):
    self.xSize = xSize
    self.ySize = ySize
    self.zSize = zSize
    self.densPerMeter = densPerMeter
    self.obstacleList = obstacleList
    
    # Calculate points in every axis
    self.nx = int(self.xSize * self.densPerMeter) + 1 # number of points in grid
    self.ny = int(self.ySize * self.densPerMeter) + 1
    self.nz = int(self.zSize * self.densPerMeter) + 1

    # Create 3d arrays
    self.vX = np.zeros((self.nz, self.ny, self.nx))
    self.vY = np.zeros((self.nz, self.ny, self.nx))
    self.vZ = np.zeros((self.nz, self.ny, self.nx))
    self.p = np.zeros((self.nz, self.ny, self.nx))

  # Convert 3d obstacles to 2d
  def convertObstaclesTo2d(self, layerMeter, isTopView = True):
    obstacleList2d = []
    if isTopView:
      for obstacle in self.obstacleList:
        if obstacle["height"] >= layerMeter:
          obstacleList2d.append(obstacle)
    else:
      for obstacle in self.obstacleList:
        # tmp list of crossingPoints
        crossingPoints = []

        # go trough every point and find if line of layer crosse it
        for i in range(len(obstacle["coordinates"])-1):
          if obstacle["coordinates"][i][1] <= layerMeter <= obstacle["coordinates"][i+1][1] or \
              obstacle["coordinates"][i][1] >= layerMeter >= obstacle["coordinates"][i+1][1]:
            # Tmp auxiliary variables A-first point, B=second point
            xA = obstacle["coordinates"][i][0]
            yA = obstacle["coordinates"][i][1]
            xB = obstacle["coordinates"][i+1][0]
            yB = obstacle["coordinates"][i+1][1]
            
            # Calculate crossing point X from mathematical equation
            # avoid division by zero
            if xB - xA == 0:
              crossingPointX = xA
            else:
              a = (yB - yA)/(xB - xA)
              if a == 0:
                crossingPointX = xA
              else:
                crossingPointX = -(((-a*xA)+yA-layerMeter)/a)

            # Add point to crossing points list
            crossingPoints.append(crossingPointX)
        
        # add buildings to obstacle list using crossing points, 
        # if more than 2 points add as separate buildings
        if len(crossingPoints) > 1:
          for i in range(0, len(crossingPoints), 2):
            tmpDict = {
              "name": obstacle["name"],
              "height": obstacle["height"],
              "coordinates": [(crossingPoints[i+1], 0), (crossingPoints[i], 0), 
                (crossingPoints[i], obstacle["height"]), (crossingPoints[i+1], obstacle["height"]), 
                (crossingPoints[i+1], 0)],
            }
            obstacleList2d.append(tmpDict)

            # Check if there are at least 2 more elements in the list
            if len(crossingPoints) < i + 4:
              break
      
    return obstacleList2d


  # Get side view from 3d array
  def getSideView2dArray(self, array3d, yLayer):
    # Declare empty array to return
    array2d = np.empty([self.nz, self.nx])

    # Convert 3d array to 2d
    for i in range(self.nz):
      for j in range(self.nx):
        array2d[i,j] = array3d[i, yLayer, j]
      
    return array2d


  # Copy layer to 3d array
  def copyLayerTo3DArray(self, array1, array2, layer, isTopView = True):
    if isTopView:
      # Copy top view array to 3d array
      for i in range(self.ny):
        for j in range(self.nx):
          self.vX[layer, i, j] += array1[i, j]
          self.vY[layer, i, j] += array2[i, j]
    else:
      for i in range(self.nz):
        for j in range(self.nx):
          self.vX[i, layer, j] += array1[i, j]
          self.vZ[i, layer, j] += array2[i, j]


  # Calculate flow -----------------------------------------------------------------------
  def calculateFlow(self):
    # Simulate top layers
    print("AF:", "Start calculating top view")
    for i in range(self.nz):
      # Get obstacles for layer top view
      obstaclesForLayer = self.convertObstaclesTo2d(i/self.densPerMeter)
      
      # Simulate layer
      topView = rays2dcalculator.Rays2dCalculator(self.xSize, self.ySize, i,
        self.densPerMeter, obstaclesForLayer)
      X, Y, x, y, pt = topView.getFlowPathArray()
      
      # Copy layer top 3d array
      self.copyLayerTo3DArray(x, y, i)
    
    # Simulate side layers
    print("AF:", "Start calculating side view")
    for i in range(self.ny):
      # get obstacles for layer side view
      obstaclesForLayer = self.convertObstaclesTo2d(i/self.densPerMeter, isTopView=False)
      
      sideView = rays2dcalculator.Rays2dCalculator(self.xSize, self.zSize, i,
        self.densPerMeter, obstaclesForLayer, isTopView=False)
      X, Z, x, z, pt = sideView.getFlowPathArray()
      
      self.copyLayerTo3DArray(x, z, i, isTopView=False)
    
    # Reduce duplications in vX array
    self.vX /= 2

    # Calculate pressure
    self.p = np.absolute(self.vX) + np.absolute(self.vY) + np.absolute(self.vZ)

    print("AF:", "Flow calculated")


  # Get top view for specified meter above ground ----------------------------------------
  def getTopViewLayerForMeter(self, meterAboveGround):
    # Calculate layer coresponding to given meter
    zLayer = int(meterAboveGround * self.densPerMeter)

    x = np.linspace(0, self.xSize, self.nx) # last point included, so exactly self.nx points
    y = np.linspace(0, self.ySize, self.ny) # last point included, so exactly self.ny points
    
    X,Y = np.meshgrid(x, y)     # makes 2-dimensional mesh grid
    array2dX = self.vX[zLayer]  # Get layers
    array2dY = self.vY[zLayer]
    array2dP = self.p[zLayer]

    # Get only obstacles from current layer
    listOf2dObstacles = self.convertObstaclesTo2d(meterAboveGround, isTopView = True)

    # Print text and display plot
    titleText = "{}m above ground ({} Z axis layer)".format(meterAboveGround, zLayer+1)
    print("AF:", titleText)
    visualize.showPlot(X, Y, array2dX, array2dY, array2dP, listOf2dObstacles, titleText)

  
  # Get side view for specified meter above ground --------------------------------------- 
  def getSideViewLayerForMeter(self, meterFromY0):
    # Calculate layer coresponding to given meter
    yLayer = int(meterFromY0 * self.densPerMeter)

    x = np.linspace(0, self.xSize, self.nx) # last point included, so exactly self.nx points
    z = np.linspace(0, self.zSize, self.nz) # last point included, so exactly self.ny points
    
    X,Z = np.meshgrid(x, z)     # makes 2-dimensional mesh grid
    array2dX = self.getSideView2dArray(self.vX, yLayer) # Get layers
    array2dZ = self.getSideView2dArray(self.vZ, yLayer)
    array2dP = self.getSideView2dArray(self.p, yLayer)

    # only obstacles from current layer
    listOf2dObstacles = self.convertObstaclesTo2d(yLayer, isTopView = False)
    
    # Print text and display plot
    titleText = "{}m from left ({} Y axis layer)".format(meterFromY0, yLayer+1)
    print("AF:", titleText)
    visualize.showPlot(X, Z, array2dX, array2dZ, array2dP, listOf2dObstacles, titleText)


  # Get flow in single array
  def getFlowArray(self):
    flowArray = []
    print(len(self.vX), len(self.vX[0]), len(self.vX[0,0]))
    for z in range(len(self.vX)):
      tmpYList = []
      for y in range(len(self.vX[0])):
        tmpXList = []
        for x in range(len(self.vX[0,0])):
          tmpXList.append((self.vX[z,y,x], self.vY[z,y,x], self.vZ[z,y,x]))
        tmpYList.append(tmpXList)
      flowArray.append(tmpYList)

    return flowArray, self.p
