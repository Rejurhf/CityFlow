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
    percentIndicator = 0
    converters.printProgress(percentIndicator)
    # Calculate rays
    for z in range(self.nz):
      for y in range(self.ny):
        if(percentIndicator+0.02 <= (z*self.ny + y)/(self.ny*self.nz)):
          percentIndicator = round(percentIndicator+0.02, 2)
          converters.printProgress(percentIndicator)
        # Declare tmp ray list
        rayPoints = []
        posX = 0
        posY = y
        posZ = z

        # Define colision point which stores point on which ray hits obstacle[||   ]
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
            posX, posY, posZ, subRayList, popCount = \
              self.getShortestRoute([posX, posY, posZ], direction="x+")
            # Pop unused points 
            if popCount > 0:
              rayPoints = rayPoints[:-popCount]
            # Merge lists
            rayPoints.extend(subRayList)
            posX += 1
        
        # Add ray to ray list
        self.rayList.append(rayPoints)
    converters.printProgress(1, end=True)

  # Create ray list go to target position
  def goToTargetPositionDetermination(self, posX, posY, posZ, colisionPos, cornerPos, targetPos):
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
            shadow = self.getColisionObstacleFrontLen(colisionPos, mode)
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
        else:
          # Go straight
          newPosX += 1

    if newPosX == posX and newPosY == posY and newPosZ == posZ:
      newPosX += 1

    return newPosX, newPosY, newPosZ, colisionPos, cornerPos, targetPos


  # Get shortest route around obstacle
  def getShortestRoute(self, colisionPos, direction="x+"):
    # Get front target position, pos of nearest edge
    targetPos, isNoRoute, mode = self.getNearestEdgePointAfterColision(
      colisionPos[0], colisionPos[1], colisionPos[2], direction="x+")

    # If no route found, return point out of map and end this ray
    if isNoRoute:
      targetPos[0] = self.nx
      return targetPos[0], targetPos[1], targetPos[2], []

    # Add start position, half obstacle front before it
    shadow = self.getColisionObstacleFrontLen(colisionPos, mode)
    shadow = shadow - int(shadow/2)
    startPos = []
    for i in range(shadow+1):
      if colisionPos[0]-(shadow-i) >= 0 and \
          not self.isPointInObstacle(colisionPos[0]-(shadow-i), colisionPos[1], colisionPos[2]):
        startPos = [colisionPos[0]-(shadow-i), colisionPos[1], colisionPos[2]]
        break
      if i == shadow and not startPos:
        startPos = [colisionPos[0]-(shadow), colisionPos[1], colisionPos[2]]

    # Populate subRayList, create route from colisionPos to targetPos [20, 18, 10] [20, 27, 10]
    subRayList = []
    tmpX = startPos[0]
    tmpY = startPos[1]
    tmpZ = startPos[2]
    while [tmpX, tmpY, tmpZ] != targetPos:
      # Flag if Y and Z axis always skips
      flowDir = 0

      for i in range(1, 3):
        # To avoid repetition
        if i == 1:
          if tmpY == targetPos[1]:
            continue
          posYZ = startPos[1]
          locMode = "y"
        else:
          if tmpZ == targetPos[2]:
            continue
          posYZ = startPos[2]
          locMode = "z"

        # If point more than 1 point away from guide line 
        # (line between corner and target) go to target
        distanceFromGuideLine = converters.getDistanceFromPointToLine(
          startPos, targetPos, [tmpX, tmpY, tmpZ], locMode)
        flowDir = (1 if posYZ < targetPos[i] else -1)
        if distanceFromGuideLine > 0.6:
          if i == 1:
            tmpY += flowDir
          else:
            tmpZ += flowDir
        else:
          tmpX += 1

      if flowDir == 0:
        tmpX += 1
      
      # Add step to subRayList
      subRayList.append([tmpX, tmpY, tmpZ])

    return targetPos[0], targetPos[1], targetPos[2], subRayList, shadow


  # Get nearest point to go forward after colision
  def getNearestEdgePointAfterColision(self, posX, posY, posZ, direction="x+"):
    shift = 0
    bestDirection = ""
    mode = ""
    # Get directions with shortest route
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

    # -1 cause shift is one step ahead
    shift -= 1

    # Determine new point position
    newPosX = posX
    newPosY = posY
    newPosZ = posZ

    # In case of many directions
    # If direction occurs only once add it to target pos
    if bestDirection.count('x') == 1:
      # Set mode to x axis have shortest route
      if not mode:
        mode = "x"
      if bestDirection[bestDirection.find('x')+1] == '+':
        newPosX += shift
      else:
        newPosX -= shift

    if bestDirection.count('y') == 1:
      if not mode:
        mode = "y"
      if bestDirection[bestDirection.find('y')+1] == '+':
        newPosY += shift
      else:
        newPosY -= shift

    if bestDirection.count('z') == 1:
      if not mode:
        mode = "z"
      if bestDirection[bestDirection.find('z')+1] == '+':
        newPosZ += shift
      else:
        newPosZ -= shift

    # In case best directions are opposite directions
    if posX == newPosX and posY == newPosY and posZ == newPosZ:
      # TODO now only go in one direction, do it to go both directions (split the ray)
      if bestDirection.count('x') > 1:
        if not mode:
          mode = "x"
        newPosX += shift
      elif bestDirection.count('y') > 1:
        if not mode:
          mode = "y"
        newPosY += shift
      else:
        if not mode:
          mode = "z"
        newPosZ += shift

    # In case of no shortest route found, send ending ray flag
    if posX == newPosX and posY == newPosY and posZ == newPosZ:
      isNoRoute = False
      return [newPosX, newPosY, newPosZ], isNoRoute, mode

    # Nearest edge position found, return it with shortest route mode
    isNoRoute = False
    return [newPosX, newPosY, newPosZ], isNoRoute, mode
  

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
  def getColisionObstacleFrontLen(self, colisionPos, mode="y"):
    # Go + Direction
    plusShift = 0
    minusShift = 0

    if mode == "y":
      yMute = 1
      zMute = 0
    else:
      yMute = 0
      zMute = 1

    while colisionPos[1]+(plusShift*yMute) < self.ny and colisionPos[2]+(plusShift*zMute) < self.nz and \
      self.isPointInObstacle(
        colisionPos[0]+1, colisionPos[1]+(plusShift*yMute), colisionPos[2]+(plusShift*zMute)):
      plusShift += 1

    while colisionPos[1]-(minusShift*yMute) >= 0 and colisionPos[2]-(minusShift*zMute) >= 0 and \
      self.isPointInObstacle(
        colisionPos[0]+1, colisionPos[1]-(minusShift*yMute), colisionPos[2]-(minusShift*zMute)):
      minusShift += 1

    return int((plusShift + minusShift)/2)


# Rays to array ------------------------------------------------------------------------------------
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

