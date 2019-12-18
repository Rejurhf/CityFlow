import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from utilities import visualize, rays2dcalculator, converters

class AirFlow2:
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

    # Create ray list
    self.rayList = []

    # Create 3d arrays
    self.v = np.zeros((self.nz, self.ny, self.nx, 3))
    self.p = np.zeros((self.nz, self.ny, self.nx))


# Calculations -------------------------------------------------------------------------------------
  # Calculate flow
  def calculateFlow(self):
    # Calculate ray list
    print("AF2:", "Create ray list")
    self.createRayList()

    # Convert rays to 3d array
    print("AF2:", "Converting rays to array")
    self.convertRaysTo3dArray()

    print("AF2: Flow calculated")


  # Calculate ray list
  def createRayList(self):
    # Calculate rays
    for z in range(self.nz):
      for y in range(self.ny):
        # Declare tmp ray list
        rayPoints = []
        posX = 0
        posY = y
        posZ = z

        # Define colision point which stores point on which ray hits obstacle
        colisionPos = []
        # Define pos on end corner of obstacle and target position
        cornerPos = []
        targetPos = []

        # Get ray route
        while 0 <= posX < self.nx and 0 <= posY < self.ny and 0 <= posZ < self.nz:
          rayPoints.append([posX,posY,posZ])

          if not self.isPointInObstacle(posX+1,posY,posZ):
            # If no obstacle ahead
            if colisionPos and (posY != colisionPos[1] or posZ != colisionPos[2]):
              posX, posY, posZ, colisionPos, cornerPos, targetPos = \
                self.goToTargetPositionDetermination(
                  posX, posY, posZ, colisionPos, cornerPos, targetPos)
            elif colisionPos and posY == colisionPos[1] and posZ == colisionPos[2]:
              # Ray in original pos delete target and sideLen
              colisionPos = []
              cornerPos = []
              targetPos = []
              posX += 1
            else: 
              posX += 1
          else:
            # Add point to colision
            colisionPos = [posX, posY, posZ]
            cornerPos = []
            targetPos = []
            # direction="x+" means, obstacle por posX+=1
            posX, posY, posZ, subRayList = self.getShortestRoute(posX, posY, posZ, direction="x+")
            rayPoints.extend(subRayList)
            posX += 1
        
        # Add ray to ray list
        self.rayList.append(rayPoints)


  # Create ray list go to target position
  def goToTargetPositionDetermination(self, posX, posY, posZ, colisionPos, cornerPos, targetPos):
    # Flag to check if sidelen was added
    isSideObs = False

    newPosX = posX
    newPosY = posY
    newPosZ = posZ

    for i in range(1, 3):
      # To avoid repetition
      if i == 1:
        posYZ = posY
        mode = "y"
      else:
        posYZ = posZ
        mode = "z"

      # Go to original position
      if posYZ != colisionPos[i]:
        flowDir = (1 if posYZ < colisionPos[i] else -1)
        # If can not go towards the target go straight 
        # (flowDir*(2-i)) = 0 if mode z 2-i and i-1 one of them is always 0 depending on the mode
        if not self.isPointInObstacle(posX, posY+(flowDir*(2-i)), posZ+(flowDir*(i-1))):
          # If can go to target go for it
          if not cornerPos:
            # Define obstacle corner pos and target pos, do it only once
            cornerPos = [posX, posY, posZ]
            # put target position, 3 deltas Y from obstacle 
            shadow = self.getColisionObstacleSize(*colisionPos)
            if shadow == 0:
              shadow = posYZ - colisionPos[i]
            targetPos = [posX + abs(shadow*3), colisionPos[1], colisionPos[2]]

          # If point more than 1 point away from guide line 
          # (line between corner and target) go to target
          distanceFromGuideLine = converters.getDistanceFromPointToLine(
            cornerPos, targetPos, [posX, posY, posZ], mode)
          if distanceFromGuideLine > 0.6:
            if i == 1:
              newPosY += flowDir
            else:
              newPosZ += flowDir
          else:
            newPosX += 1
            isSideObs = True
        else:
          # Go straight
          newPosX += 1
          isSideObs = True

    if newPosX == posX and newPosY == posY and newPosZ == posZ:
      newPosX += 1

    return newPosX, newPosY, newPosZ, colisionPos, cornerPos, targetPos


  # Check if point is in obstacle
  def isPointInObstacle(self, posX, posY, posZ):
    for obstacle in self.obstacleList:
      # Convert layer number to metres, create the point and polygon 
      tmpPoint = Point(posX/self.densPerMeter, posY/self.densPerMeter)
      polygon = Polygon(obstacle["coordinates"])

      # If point on the edge of polygon
      if polygon.exterior.distance(tmpPoint) == 0 and posZ/self.densPerMeter <= obstacle["height"]:
        return True

      # If in obstacle (check height) return True
      if polygon.contains(tmpPoint) and posZ/self.densPerMeter <= obstacle["height"]:
        return True
    return False


  # Get size of obstacle to measure shadow
  def getColisionObstacleSize(self, posX, posY, posZ, mode="y"):
    # Go + Direction
    plusShift = 0
    minusShift = 0

    if mode == "y":
      yMute = 1
      zMute = 0
    else:
      yMute = 0
      zMute = 1

    while self.isPointInObstacle(posX+1, posY+(plusShift*yMute), posZ+(plusShift*zMute)):
      plusShift += 1

    while self.isPointInObstacle(posX+1, posY-(minusShift*yMute), posZ-(minusShift*zMute)):
      minusShift += 1

    return (plusShift + minusShift)/2


  # Get shortest route around obstacle
  def getShortestRoute(self, posX, posY, posZ, direction="x+"):
    shift = 0
    bestDirection = ""
    # Get direction with shortest route
    while not bestDirection and (posX+shift<self.nx or posX-shift>=0 or \
        posY+shift<self.ny or posY-shift>=0 or posZ+shift<self.nz or posZ-shift>=0):
      if direction == "x+":
        if posY+shift < self.ny and not self.isPointInObstacle(posX+1, posY+shift, posZ):
          bestDirection += "y+"
        if posY-shift >= 0 and not self.isPointInObstacle(posX+1, posY-shift, posZ):
          bestDirection += "y-"
        if posZ+shift < self.nz and not self.isPointInObstacle(posX+1, posY, posZ+shift):
          bestDirection += "z+"
        if posZ-shift >= 0 and not self.isPointInObstacle(posX+1, posY, posZ-shift):
          bestDirection += "z-"
      shift += 1

    # Fix shift error
    shift -= 1

    # Determine new point position
    subRayList =[]
    newPosX = posX
    newPosY = posY
    newPosZ = posZ
    if len(bestDirection) > 2:
      # In case of many directions
      # If direction occurs only once add it to raylist
      if bestDirection.count('x') == 1:
        if bestDirection[bestDirection.find('x')+1] == '+':
          newPosX += shift
        else:
          newPosX -= shift
      if bestDirection.count('y') == 1:
        if bestDirection[bestDirection.find('y')+1] == '+':
          newPosY += shift
        else:
          newPosY -= shift
      if bestDirection.count('z') == 1:
        if bestDirection[bestDirection.find('z')+1] == '+':
          newPosZ += shift
        else:
          newPosZ -= shift

      # In case best directions are opposite directions
      if posX == newPosX and posY == newPosY and posZ == newPosZ:
        # TODO now only go in one direction, do it to go both directions
        if bestDirection.count('x') > 1:
          newPosX += shift
        elif bestDirection.count('y') > 1:
          newPosY += shift
        else:
          newPosZ += shift
    elif len(bestDirection) == 2:
      # In case of one direction
      if bestDirection.count('x') == 1:
        if bestDirection[1] == '+':
          newPosX += shift
        else:
          newPosX -= shift
      if bestDirection.count('y') == 1:
        if bestDirection[1] == '+':
          newPosY += shift
        else:
          newPosY -= shift
      if bestDirection.count('z') == 1:
        if bestDirection[1] == '+':
          newPosZ += shift
        else:
          newPosZ -= shift
    else:
      # In case of no directions, give position out the map
      newPosX = self.nx
      return newPosX, newPosY, newPosZ, subRayList

    # Populate subRayList
    tmpX = posX
    tmpY = posY
    tmpZ = posZ
    for i in range(0, shift):
      # Determine next step
      if tmpX != newPosX:
        tmpX += (1 if tmpX < newPosX else -1)
      if tmpY != newPosY:
        tmpY += (1 if tmpY < newPosY else -1)
      if tmpZ != newPosZ:
        tmpZ += (1 if tmpZ < newPosZ else -1)
      
      # Add step to subRayList
      subRayList.append([tmpX, tmpY, tmpZ])

    return newPosX, newPosY, newPosZ, subRayList 


  # Convert rays to 3d array
  def convertRaysTo3dArray(self):
    # Get ray
    for ray in self.rayList:
      # Go trough points starting from second
      for i in range(1, len(ray)-1):
        posX = ray[i][0]
        posY = ray[i][1]
        posZ = ray[i][2]
        
        # Initialize starting point with 1, i is index of point in ray
        if i == 1:
          self.v[posZ,posY,0,0] = 1

        # Find next direction
        if ray[i+1][0] != posX:
          self.v[posZ,posY,posX,0] += ray[i+1][0] - posX
        if ray[i+1][1] != posY:
          self.v[posZ,posY,posX,1] += ray[i+1][1] - posY
        if ray[i+1][2] != posZ:
          self.v[posZ,posY,posX,2] += ray[i+1][2] - posZ
      
      # Add last position same value as previous
      self.v[ray[-1][2],ray[-1][1],ray[-1][0]] = self.v[ray[-2][2],ray[-2][1],ray[-2][0]]

    # Create pressure array
    for z in range(self.nz):
      for y in range(self.ny):
        for x in range(self.nx):
          self.p[z,y,x] =  sum(abs(v) for v in self.v[z,y,x])



# Visualizations ----------------------------------------------------------------------------------- 
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


  # Get top view for specified meter above ground ----------------------------------------
  def getTopViewLayerForMeter(self, meterAboveGround):
    # Calculate layer coresponding to given meter
    zLayer = int(meterAboveGround * self.densPerMeter)

    x = np.linspace(0, self.xSize, self.nx) # last point included, so exactly self.nx points
    y = np.linspace(0, self.ySize, self.ny) # last point included, so exactly self.ny points
    
    X,Y = np.meshgrid(x, y)     # makes 2-dimensional mesh grid
    # Get layers
    array2dX = self.v[zLayer,:,:,0]
    array2dY = self.v[zLayer,:,:,1]
    array2dP = self.p[zLayer,:,:]

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
    # Get layers
    array2dX = self.v[:,yLayer,:,0]
    array2dZ = self.v[:,yLayer,:,2]
    array2dP = self.p[:,yLayer,:]

    # only obstacles from current layer
    listOf2dObstacles = self.convertObstaclesTo2d(yLayer, isTopView = False)
    
    # Print text and display plot
    titleText = "{}m from left ({} Y axis layer)".format(meterFromY0, yLayer+1)
    print("AF:", titleText)
    visualize.showPlot(X, Z, array2dX, array2dZ, array2dP, listOf2dObstacles, titleText)

