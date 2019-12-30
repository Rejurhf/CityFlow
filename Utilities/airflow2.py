import numpy as np
import math
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

    # Obstacle array
    self.obstacle = np.zeros((self.nz, self.ny, self.nx))


# Calculations -------------------------------------------------------------------------------------
  # Calculate flow
  def calculateFlow(self):
    # Generate obstacle array
    print("[AF2]", "Create obstacle array")
    self.createObstacleArray()

    # Calculate ray list
    print("[AF2]", "Create ray list")
    self.createRayList()

    # Convert rays to 3d array
    print("[AF2]", "Converting rays to array")
    self.convertRaysTo3dArray()

    print("[AF2] Flow calculated")


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

        # Define colision point which stores point on which ray hits obstacle
        colisionPos = []
        targetPosition = []
        # Stage indicator 0 -no colision, 1 - front, 2 - side, 3 - back
        stage = 0
        stageCount = 0
        breakFlag = False

        # Get ray route
        while 0 <= posX < self.nx and 0 <= posY < self.ny and 0 <= posZ < self.nz:
          # If normal flow add position normally
          rayPoints.append([posX,posY,posZ])

          # Flow if no obstacle involved
          if not colisionPos and not self.isPointInObstacle(posX+1,posY,posZ):
            # No obstacle ahead go straight
            posX += 1
          elif not colisionPos and self.isPointInObstacle(posX+1,posY,posZ):
            # Add point to colision
            colisionPos = [posX, posY, posZ]
            targetPosition = colisionPos.copy()
            stage = 1
          
          # edge shift parameter
          edgeShift = 0
          # Flow if obstacle involved
          while stage > 0:
            if stage == 1 and colisionPos:
              # direction="x+" means, obstacle por posX+=1
              posX, posY, posZ, subRayList, popCount, edgeShift = \
                self.fGetFrontRay([posX, posY, posZ], direction="x+")

              if posX >= self.nx:
                breakFlag = True
                break
              # Pop unused points 
              if popCount > 0:
                rayPoints = rayPoints[:-popCount]
              # Merge lists
              rayPoints.extend(subRayList)
              # New stage indicator
              stage = 2
            elif stage == 2 and colisionPos:
              # Calculate side flow
              posX, posY, posZ, subRayList = \
                self.sGetSideRay([posX, posY, posZ], colisionPos, edgeShift)
              rayPoints.extend(subRayList)
              # New stage indicator
              stage = 3
            elif stage == 3 and colisionPos:
              # Calculate back flow
              posX, posY, posZ, subRayList, colisionPos = \
                self.bGetBackRay([posX, posY, posZ], targetPosition)
              rayPoints.extend(subRayList)
              # Clean out and stage
              if targetPosition == colisionPos and not self.isPointInObstacle(posX+1,posY,posZ):
                # No colision occurred and next position is not coliding
                colisionPos = []
                targetPosition = []
                posX += 1
                stage = 0
              elif self.isPointInObstacle(posX+1,posY,posZ):
                # No colision but next position is coliding
                # targetPosition = colisionPos.copy()
                colisionPos = [posX, posY, posZ]
                stage = 1
                stageCount += 1
              else:
                # Colision occurred
                stage = 1      
                stageCount += 1

            if stageCount > 10:
              print(rayPoints[0])
              breakFlag = True
              break
          if breakFlag:
            stageCount = 0
            breakFlag = False
            break
        
        # self.isRayInObstacle(rayPoints)
        # Add ray to ray list
        self.rayList.append(rayPoints)
    converters.printProgress(1, end=True)
  
  # Get flow after obstacle
  def bGetBackRay(self, startPos, colisionPos, direction="x+"):
    # Determine obstacle size and multiply it by 3 to create shadow 
    shift = 3 * self.getColisionObstacleFrontLen(
      [startPos[0]-1,colisionPos[1], colisionPos[2]], flowMode="x-")

    targetPos = [startPos[0]+shift, colisionPos[1], colisionPos[2]]

    # Populate subRayList, create route from colisionPos to targetPos 
    endPos, subRayList, isColision = self.goFromStartToTarget(startPos, targetPos)

    # If colision
    if isColision:
      return endPos[0], endPos[1], endPos[2], subRayList, endPos
    # If no colision
    return endPos[0], endPos[1], endPos[2], subRayList, colisionPos


  # Get side flow (between front and back of the obstacle)
  def sGetSideRay(self, startPos, colisionPos, startShift, direction="x+"):
    targetPos, sideLen, mode = \
      self.sGetEndOfObstacleSide(startPos, colisionPos, startShift, direction)

    yMute = 0
    zMute = 0
    if mode.count('y') == 1:
      yMute = 1
      if mode[mode.find('y')+1] == '+':
        yMute = -yMute
    elif mode.count('z') == 1:
      zMute = 1
      if mode[mode.find('z')+1] == '+':
        zMute = -zMute
    
    # Calculate sub shift
    shiftS = int(sideLen/8)
    # Create sub target
    subTargetPos = [startPos[0]+int(sideLen/4), 
      targetPos[1]+(yMute*shiftS), targetPos[2]+(zMute*shiftS)]

    # Populate subRayList, create route from startPos to subTargetPos 
    subStartPos, subRayList, isColision = self.goFromStartToTarget(startPos, subTargetPos)
    subFlowList = subRayList
    # Populate subRayList, create route from subStartPos to targetPos 
    targetPos, subRayList, isColision = self.goFromStartToTarget(subStartPos, targetPos)
    subFlowList.extend(subRayList)

    return targetPos[0], targetPos[1], targetPos[2], subFlowList


  # Get nearest point after obstacle
  def sGetEndOfObstacleSide(self, startPos, colisionPos, startShift, direction="x+"):

    # Shift indicator
    shift = 1

    # Get colision mode
    # Take into account colision mode
    mode = ""
    shiftY = 0
    shiftZ = 0
    if startPos[1] < colisionPos[1]:
      mode += "y+"
      shiftY += (startShift + 1)
    elif startPos[1] > colisionPos[1]:
      mode += "y-"
      shiftY -= (startShift + 1)
    if startPos[2] < colisionPos[2]:
      mode += "z+"
      shiftZ += (startShift + 1)
    elif startPos[2] > colisionPos[2]:
      mode += "z-"
      shiftZ -= (startShift + 1) 

    # Go to end of obstacle
    while self.isPointInObstacle(startPos[0]+shift, startPos[1]+shiftY, startPos[2]+shiftZ) and \
        not self.isPointInObstacle(startPos[0]+shift, startPos[1], startPos[2]):
      shift += 1

    return [startPos[0]+shift, startPos[1], startPos[2]], shift, mode
      

  # Get shortest route around obstacle
  def fGetFrontRay(self, colisionPos, direction="x+"):
    # Get front target position, pos of nearest edge
    targetPos, isNoRoute, mode = self.fGetNearestEdgePointAfterColision(
      colisionPos[0], colisionPos[1], colisionPos[2], direction="x+")

    # If no route found, return point out of map and end this ray
    if isNoRoute:
      targetPos[0] = self.nx
      return targetPos[0], targetPos[1], targetPos[2], [], 0, 0

    # Add start position, half obstacle front before it
    shadow = self.getColisionObstacleFrontLen(colisionPos, mode)
    shadow = shadow - int(shadow/2)

    # Move start back
    startPos = []
    for i in range(shadow+1):
      if colisionPos[0]-(shadow-i) >= 0 and \
          not self.isPointInObstacle(colisionPos[0]-(shadow-i), colisionPos[1], colisionPos[2]):
        startPos = [colisionPos[0]-(shadow-i), colisionPos[1], colisionPos[2]]
        break
      if i == shadow and not startPos:
        startPos = [colisionPos[0]-(shadow), colisionPos[1], colisionPos[2]]

    # Move target pos depending of colision position
    # Calculate distance between colisin and target
    startTargetDist = \
      int(math.sqrt((colisionPos[1]-targetPos[1])**2 + (colisionPos[2]-targetPos[2])**2))
    # Calculate target shift
    targetShift = int(((1.8*shadow)-startTargetDist)/2)
    if targetShift < 0:
      targetShift = 0

    # Add shift to target
    if mode.count('y') == 1:
      if mode[mode.find('y')+1] == '+':
        targetPos[1] += targetShift
      else: 
        targetPos[1] -= targetShift
    elif mode.count('z') == 1:
      if mode[mode.find('z')+1] == '+':
        targetPos[2] += targetShift
      else:
        targetPos[2] -= targetShift

    # Populate subRayList, create route from colisionPos to targetPos 
    targetPos, subRayList, isColision = self.goFromStartToTarget(startPos, targetPos)

    return targetPos[0], targetPos[1], targetPos[2], subRayList, shadow, targetShift


  # Get nearest point to go forward after colision
  def fGetNearestEdgePointAfterColision(self, posX, posY, posZ, direction="x+"):
    shift = 0
    bestDirection = ""
    mode = ""
    # Define lock if there is barier not to cross by search, lock = [y+ lock, y-, z+, z-]
    lock = [False, False, False, False]
    # Get directions with shortest route
    while not bestDirection and (posX+shift<self.nx or posX-shift>=0 or \
        posY+shift<self.ny or posY-shift>=0 or posZ+shift<self.nz or posZ-shift>=0):
      if direction == "x+":
        if not lock[0] and posY+shift < self.ny and \
            not self.isPointInObstacle(posX+1, posY+shift, posZ):
          bestDirection += "y+"
        elif not lock[0] and (posY+shift >= self.ny or self.isPointInObstacle(posX, posY+shift, posZ)):
          lock[0] = True
        if not lock[1] and posY-shift >= 0 and \
            not self.isPointInObstacle(posX+1, posY-shift, posZ):
          bestDirection += "y-"
        elif not lock[1] and (posY-shift < 0 or self.isPointInObstacle(posX, posY-shift, posZ)):
          lock[1] = True
        if not lock[2] and posZ+shift < self.nz and \
            not self.isPointInObstacle(posX+1, posY, posZ+shift):
          bestDirection += "z+"
        elif not lock[2] and (posZ+shift >= self.nz or self.isPointInObstacle(posX, posY, posZ+shift)):
          lock[2] = True
        if not lock[3] and posZ-shift >= 0 and \
            not self.isPointInObstacle(posX+1, posY, posZ-shift):
          bestDirection += "z-"
        elif not lock[3] and (posZ-shift < 0 or self.isPointInObstacle(posX, posY, posZ-shift)):
          lock[3] = True

      # If barier in every direction
      if lock == [True, True, True, True]:
        break
      shift += 1

    # In case of no shortest route found, send ending ray flag
    if not bestDirection:
      isNoRoute = True
      return [posX, posY, posZ], isNoRoute, mode

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
        mode += "+"
      else:
        newPosX -= shift
        mode += "-"

    if bestDirection.count('y') == 1:
      if not mode:
        mode = "y"
      if bestDirection[bestDirection.find('y')+1] == '+':
        newPosY += shift
        mode += "+"
      else:
        newPosY -= shift
        mode += "-"

    if bestDirection.count('z') == 1:
      if not mode:
        mode = "z"
      if bestDirection[bestDirection.find('z')+1] == '+':
        newPosZ += shift
        mode += "+"
      else:
        newPosZ -= shift
        mode += "-"

    # In case best directions are opposite directions
    if posX == newPosX and posY == newPosY and posZ == newPosZ:
      # TODO now only go in one direction, do it to go both directions (split the ray)
      if bestDirection.count('x') > 1:
        if not mode:
          mode = "x+"
        newPosX += shift
      elif bestDirection.count('y') > 1:
        if not mode:
          mode = "y+"
        newPosY += shift
      else:
        if not mode:
          mode = "z+"
        newPosZ += shift

    # Nearest edge position found, return it with shortest route mode
    isNoRoute = False
    return [newPosX, newPosY, newPosZ], isNoRoute, mode
  

  # Go from start to target
  def goFromStartToTarget(self, startPos, targetPos):
    # Populate subRayList, create route from colisionPos to targetPos
    subRayList = []
    tmpX = startPos[0]
    tmpY = startPos[1]
    tmpZ = startPos[2]
    while [tmpX, tmpY, tmpZ] != [targetPos[0], targetPos[1], targetPos[2]]:
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
      
      # If colision return 
      if self.isPointInObstacle(tmpX, tmpY, tmpZ):
        endPos = subRayList[-1] if subRayList else targetPos.copy()
        return endPos, subRayList, True
      
      # Add step to subRayList
      subRayList.append([tmpX, tmpY, tmpZ])
    

    endPos = targetPos.copy()
    return endPos, subRayList, False


  # Create obstacle array
  def createObstacleArray(self):
    count = 0
    numOfObstacle = len(self.obstacleList)
    percentIndicator = 0
    converters.printProgress(percentIndicator)
    for obstacle in self.obstacleList:
      # Print progress
      count += 1
      if (percentIndicator+0.02) <= (count/numOfObstacle):
        percentIndicator = round(percentIndicator+0.02, 2)
        converters.printProgress(percentIndicator)

      # Convert layer number to metres, create the point and polygon
      polygon = Polygon(obstacle["coordinates"])

      tmpX = int(obstacle["coordinates"][0][0]*self.densPerMeter)
      tmpY = int(obstacle["coordinates"][0][1]*self.densPerMeter)
      tmpZ = int((obstacle["height"]-1)*self.densPerMeter)

      toVisitPoints = [[tmpX+x,tmpY+y,tmpZ+z] for x in [-1,0,1] for y in [-1,0,1] for z in [-1,0,1]]
      visitedPoints = []

      # Go troughs all to visit points
      while toVisitPoints:
        curPoint = toVisitPoints.pop(0)
        visitedPoints.append(curPoint)

        if self.isPointInBoundaries(curPoint) and \
            (curPoint[2]/self.densPerMeter) <= obstacle["height"]:
          tmpPoint = Point(curPoint[0]/self.densPerMeter, curPoint[1]/self.densPerMeter)
          if polygon.exterior.distance(tmpPoint) == 0 or polygon.contains(tmpPoint):
            self.obstacle[curPoint[2],curPoint[1],curPoint[0]] = 1

            subVisitList = [[curPoint[0]+x,curPoint[1]+y,curPoint[2]+z] 
              for x in [-1,0,1] for y in [-1,0,1] for z in [-1,0,1]]
            for tmp in subVisitList:
              if tmp not in toVisitPoints and tmp not in visitedPoints:
                toVisitPoints.append(tmp)
    converters.printProgress(1, end=True)

  # Is point in boundaries check
  def isPointInBoundaries(self, point):
    if point[0] >= 0 and point[1] >= 0 and point[2] >= 0 and \
        point[0] < self.nx and point[1] < self.ny and point[2] < self.nz:
      return True
    return False


  # Check if point is in obstacle
  def isPointInObstacle(self, posX, posY, posZ):
    # for obstacle in self.obstacleList:
    #   # Convert layer number to metres, create the point and polygon 
    #   tmpPoint = Point(posX/self.densPerMeter, posY/self.densPerMeter)
    #   polygon = Polygon(obstacle["coordinates"])

    #   # If point on the edge of polygon
    #   if polygon.exterior.distance(tmpPoint) == 0 and posZ/self.densPerMeter <= obstacle["height"]:
    #     return True

    #   # If in obstacle (check height) return True
    #   if polygon.contains(tmpPoint) and posZ/self.densPerMeter <= obstacle["height"]:
    #     return True
    # return False
    if posX >= self.nx or posX < 0 or posY >= self.ny or posY < 0 or posZ >= self.nz or posZ < 0:
      return False
    if self.obstacle[posZ,posY,posX] == 1:
      return True
    return False


  # Get size of obstacle to measure shadow
  def getColisionObstacleFrontLen(self, colisionPos, mode="y", flowMode = "x+"):
    # Go + Direction
    plusShift = 0
    minusShift = 0

    if mode == "y":
      yMute = 1
      zMute = 0
    else:
      yMute = 0
      zMute = 1

    # X flow direction
    if flowMode == "x+":
      delta = 1
    else:
      delta = -1

    while colisionPos[1]+(plusShift*yMute) < self.ny and colisionPos[2]+(plusShift*zMute) < self.nz and \
      self.isPointInObstacle(
        colisionPos[0]+delta, colisionPos[1]+(plusShift*yMute), colisionPos[2]+(plusShift*zMute)):
      plusShift += 1

    while colisionPos[1]-(minusShift*yMute) >= 0 and colisionPos[2]-(minusShift*zMute) >= 0 and \
      self.isPointInObstacle(
        colisionPos[0]+delta, colisionPos[1]-(minusShift*yMute), colisionPos[2]-(minusShift*zMute)):
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

        if posX >= self.nx:
          continue
        if posY >= self.ny:
          continue
        if posZ >= self.nz:
          continue
        
        # Initialize starting point with 1, i is index of point in ray
        if i == 1:
          self.v[posZ,posY,0,0] = 1

        # Find next direction
        if ray[i+1][0] != posX:
          # Add go direction
          self.v[posZ,posY,posX,0] += ray[i+1][0] - posX
          # If go in multiple sides divide it by number of sides
          if ray[i+1][1] != posY and ray[i+1][2] != posZ:
            self.v[posZ,posY,posX,0] /= 3
          elif ray[i+1][1] != posY or ray[i+1][2] != posZ:
            self.v[posZ,posY,posX,0] /= 2
        if ray[i+1][1] != posY:
          self.v[posZ,posY,posX,1] += ray[i+1][1] - posY
          if ray[i+1][0] != posX and ray[i+1][2] != posZ:
            self.v[posZ,posY,posX,1] /= 3
          elif ray[i+1][0] != posX or ray[i+1][2] != posZ:
            self.v[posZ,posY,posX,1] /= 2
        if ray[i+1][2] != posZ:
          self.v[posZ,posY,posX,2] += ray[i+1][2] - posZ
          if ray[i+1][0] != posX and ray[i+1][1] != posY:
            self.v[posZ,posY,posX,2] /= 3
          elif ray[i+1][0] != posX or ray[i+1][1] != posY:
            self.v[posZ,posY,posX,2] /= 2
      
      # Add last position same value as previous
      if ray[-1][0] < self.nx and ray[-2][0] < self.nx:
        self.v[ray[-1][2],ray[-1][1],ray[-1][0]] = self.v[ray[-2][2],ray[-2][1],ray[-2][0]]

    # Create pressure array
    for z in range(self.nz):
      for y in range(self.ny):
        for x in range(self.nx):
          self.p[z,y,x] =  sum(abs(v) for v in self.v[z,y,x])


  # Create ray dictionary list
  def getRayFlowList(self):
    rayDictList = []
    for ray in self.rayList:
      # Create Dict for ray
      rayName = "Ray {}_{}_{}|{}".format(ray[0][0], ray[0][1], ray[0][1], len(ray))
      tmpDict = {
        "name": rayName,
        "x": ray[0][0],
        "y": ray[0][1],
        "z": ray[0][2],
        "layerpermeter": 1/self.densPerMeter,
        "positions": ray,
      }
      rayDictList.append(tmpDict)
    return rayDictList

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
    print("AF:", "Show view", titleText)
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
    print("AF:", "Show view", titleText)
    visualize.showPlot(X, Z, array2dX, array2dZ, array2dP, listOf2dObstacles, titleText)

