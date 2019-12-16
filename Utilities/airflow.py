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
    counter = 0
    for i in range(self.nz):
      if i/self.nz>=counter:
        print("{}%".format(int(counter*100)))
        counter += 0.2
      # Get obstacles for layer top view
      obstaclesForLayer = self.convertObstaclesTo2d(i/self.densPerMeter)
      
      # Simulate layer
      topView = rays2dcalculator.Rays2dCalculator(self.xSize, self.ySize, i,
        self.densPerMeter, obstaclesForLayer)
      X, Y, x, y, pt = topView.getFlowPathArray()
      
      # Copy layer top 3d array
      self.copyLayerTo3DArray(x, y, i)
    
    # Simulate side layers
    counter = 0
    print("AF:", "Start calculating side view")
    for i in range(self.ny):
      if i/self.ny>=counter:
        print("{}%".format(int(counter*100)))
        counter += 0.2
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
    
    for z in range(len(self.vX)):
      tmpYList = []
      for y in range(len(self.vX[0])):
        tmpXList = []
        for x in range(len(self.vX[0,0])):
          tmpXList.append((self.vX[z,y,x], self.vY[z,y,x], self.vZ[z,y,x]))
        tmpYList.append(tmpXList)
      flowArray.append(tmpYList)

    return flowArray, self.p


  def getRaysFromFlowArray(self, inFlowArray = [], scopeMeter = 2):
    print("AF:", "Geting Flow Rays")
    
    # check if array is passed if not get new one
    if not inFlowArray:
      flowArray, p = self.getFlowArray()
      del p
    else:
      flowArray = inFlowArray

    # Calculate constants
    flowArrayLenX = len(flowArray[0][0])
    flowArrayLenY = len(flowArray[0])
    flowArrayLenZ = len(flowArray)
    
    # Convert meterPerRay to layerPerRay  
    scope = int(scopeMeter * self.densPerMeter)

    # Calculate sub arrays len if array length can not be divided by scope
    if scope > 0:
      tmpYLen = int(flowArrayLenY / ((scope*2)+1))
      tmpZLen = int(flowArrayLenZ / ((scope*2)+1))
      
      if flowArrayLenZ % ((scope*2)+1) != 0:
        tmpZLen += 1
    
      if flowArrayLenY % ((scope*2)+1) != 0:
        tmpYLen += 1
    else:
      tmpYLen = flowArrayLenY
      tmpZLen = flowArrayLenZ


    # Calculate Ray path
    rayList = []

    for zs in range(tmpZLen):
      for ys in range(tmpYLen):
        posList = []
        startX = 0
        startY = scope + (((2*scope)+1)*ys)
        startZ = scope + (((2*scope)+1)*zs)
        
        # Check if starting pos in array
        if startY >= flowArrayLenY:
          startY = flowArrayLenY - 1
        if startZ >= flowArrayLenZ:
          startZ = flowArrayLenZ - 1 


        currPos = [startX, startY, startZ]

        # Start flow for ray
        while True:
          posList.append((currPos[0], currPos[1], currPos[2]))
          tmpValX = 0
          tmpValY = 0
          tmpValZ = 0
          posCalcCount = 0
          for z in range(-scope, scope+1):
            for y in range(-scope, scope+1):
              for x in range(-scope, scope+1):
                tmpArrayX = (currPos[0] + x)
                tmpArrayY = (currPos[1] + y)
                tmpArrayZ = (currPos[2] + z)

                # if out of array then continue
                if tmpArrayX < 0 or tmpArrayZ < 0 or tmpArrayZ < 0 or \
                    tmpArrayX >= flowArrayLenX or tmpArrayY >= flowArrayLenY or \
                    tmpArrayZ >= flowArrayLenZ:
                  continue
                elif flowArray[z][y][x][0] == 0 and flowArray[z][y][x][1] == 0 and \
                    flowArray[z][y][x][2] == 0:
                  # if all 0 then continue
                  continue
                else:
                  posCalcCount += 1
                  tmpValX += flowArray[tmpArrayZ][tmpArrayY][tmpArrayX][0]
                  tmpValY += flowArray[tmpArrayZ][tmpArrayY][tmpArrayX][1]
                  tmpValZ += flowArray[tmpArrayZ][tmpArrayY][tmpArrayX][2]
                  
          # Mean value in scope
          if posCalcCount == 0:
            break
          tmpValX /= posCalcCount
          tmpValY /= posCalcCount
          tmpValZ /= posCalcCount

          # Determine action
          if tmpValX == 0 and tmpValY == 0 and tmpValZ == 0:
            break

          newPos = self.determineNextRayPosition(tmpValX, tmpValY, tmpValZ, currPos)
          
          if newPos[0] > flowArrayLenX or newPos[0] < 0 or newPos[1] > flowArrayLenY or \
              newPos[1] < 0 or newPos[2] > flowArrayLenZ or newPos[2] < 0:
            break
          
          # TODO sprawdzenie czy dana pozycja jest już na liście
          currPos = newPos
        
        # Create Dict for ray
        rayName = "Ray {}_{}_{}|{}".format(startX, startY, startZ, len(posList))
        tmpDict = {
          "name": rayName,
          "x": startX,
          "y": startY,
          "z": startZ,
          "layerpermeter": 1/self.densPerMeter,
          "positions": posList,
        }
        rayList.append(tmpDict)
    
    return rayList

  # Determine new position of ray using values from previous position ----------------------------
  def determineNextRayPosition(self, valX, valY, valZ, currPos):
    # create new pos
    newPos = currPos

    # if valX the bigest add 1 to x and check if others should be added
    if abs(valX) > abs(valY) and abs(valX) > abs(valZ):
      # Move in x pos
      if valX > 0:
        newPos[0] += 1
      else:
        newPos[0] -= 1

      # check if move in y
      if abs(valY) >= abs(valX)/2:
        if valY > 0:
          newPos[1] += 1
        else:
          newPos[1] -= 1
      
      # check if move in z
      if abs(valZ) >= abs(valX)/2:
        if valZ > 0:
          newPos[2] += 1
        else:
          newPos[2] -= 1
    elif abs(valY) > abs(valX) and abs(valY) > abs(valZ):
      # Move in Y pos
      if valY > 0:
        newPos[1] += 1
      else:
        newPos[1] -= 1

      # check if move in XS
      if abs(valX) >= abs(valY)/2:
        if valX > 0:
          newPos[0] += 1
        else:
          newPos[0] -= 1
      
      # check if move in z
      if abs(valZ) >= abs(valY)/2:
        if valZ > 0:
          newPos[2] += 1
        else:
          newPos[2] -= 1
    else:
      # Move in Z pos
      if valZ > 0:
        newPos[2] += 1
      else:
        newPos[2] -= 1

      # check if move in X
      if abs(valX) >= abs(valZ)/2:
        if valX > 0:
          newPos[0] += 1
        else:
          newPos[0] -= 1
      
      # check if move in z
      if abs(valY) >= abs(valZ)/2:
        if valY > 0:
          newPos[1] += 1
        else:
          newPos[1] -= 1
    return newPos