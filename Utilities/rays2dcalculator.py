import numpy as np
import math as mth

class Rays2dCalculator:  
  def __init__(self, xSize, ySize, densPerMeter, obstacleList):
    self.xSize = xSize
    self.ySize = ySize
    self.densPerMeter = densPerMeter
    self.obstacleList = obstacleList


  # Is point in obstacle check ---------------------------------------------------------
  def isPointInObstacle(self, point):
    for obstacle in self.obstacleList:
      # Calculate obstacle borders
      leftBorder = mth.ceil(obstacle[0] * self.densPerMeter)
      rightBorder = mth.floor((obstacle[0] + obstacle[1]) * self.densPerMeter)
      bottomBorder = mth.ceil(obstacle[2] * self.densPerMeter)
      topBorder = mth.floor((obstacle[2] + obstacle[3]) * self.densPerMeter) 

      # Return true if point is in obstacle else return false
      if leftBorder <= point[0] <= rightBorder and bottomBorder <= point[1] <= topBorder:
        return True
    return False


  # Is point in obstacle of Index check ------------------------------------------------
  def isPointInObstacleOfIndex(self, point, obstacleIndex):
    # get obstacle from obstacle list
    curObstacle = self.obstacleList[obstacleIndex]

    # Calculate obstacle borders
    leftBorder = mth.ceil(curObstacle[0] * self.densPerMeter)
    rightBorder = mth.floor((curObstacle[0] + curObstacle[1]) * self.densPerMeter)
    bottomBorder = mth.ceil(curObstacle[2] * self.densPerMeter)
    topBorder = mth.floor((curObstacle[2] + curObstacle[3]) * self.densPerMeter) 

    # Return true if point is in obstacle else return false
    if leftBorder <= point[0] <= rightBorder and bottomBorder <= point[1] <= topBorder:
      return True
    return False


  # Get shortest route for top array ---------------------------------------------------
  def getShortestRoute(self, pointPos, isSideArray = False):
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
      if not self.isPointInObstacle((upPosX+1, upPosY)):
        upPosX += 1
      elif not self.isPointInObstacle((upPosX, upPosY+1)):
        upPosY += 1
      else:
        upPosX -= 1

    # try to go down
    while downPosX == pointPos[0]:
      downVisitedList.append((downPosX, downPosY))
      if not self.isPointInObstacle((downPosX+1, downPosY)):
        downPosX += 1
      elif not self.isPointInObstacle((downPosX, downPosY-1)):
        downPosY -= 1
      else:
        downPosX -= 1

      # Condition to avoid going under the building
      if downPosY < 0 and isSideArray:
        return upPosX, upPosY, upVisitedList

    # get shorter route and return
    if len(downVisitedList) > len(upVisitedList):
      return upPosX, upPosY, upVisitedList
    else:
      return downPosX, downPosY, downVisitedList 


  # Determine target ray position ------------------------------------------------------
  def determineTarget(self, pointPos):
    nearObsIndex = 0

    # find nearest obstacle checking them one by one
    for i in range(len(self.obstacleList)):
      if self.isPointInObstacleOfIndex(pointPos, i):
        nearObsIndex = i

    # calculate middle of obstacle y position
    nearObs = self.obstacleList[nearObsIndex]
    # centerOfObstacle = int((nearObs[2] + (nearObs[3]/2)) * self.densPerMeter)
    target = pointPos[1]
    return target


  # Calculate top array ----------------------------------------------------------------
  def getFlowPathTopArray(self):
    nx = int(self.xSize * self.densPerMeter) + 1 # number of points in grid
    ny = int(self.ySize * self.densPerMeter) + 1

    x = np.linspace(0,self.xSize,nx) # last point included, so exactly nx points
    y = np.linspace(0,self.ySize,ny) # last point included, so exactly ny points
    X,Y = np.meshgrid(x,y)    # makes 2-dimensional mesh grid

    v = np.zeros((ny, nx))
    u = np.zeros((ny, nx))  # for u-velocity I initialise to 1 everywhere

    
    for ray in range(ny):
      visitedPoints = []
      
      # Initial ray position
      posX = 0
      posY = ray
      targetY = -1

      while posX < nx and 0 <= posY <= ny:
        visitedPoints.append((posX, posY))

        # Determine action
        if not self.isPointInObstacle((posX+1,posY)):
          # if point x+1 is not obstacle go right
          if len(visitedPoints) > 1 and targetY >= 0 and targetY != posY and \
              visitedPoints[-1][1] == visitedPoints[-2][1] and \
              visitedPoints[-1][1] == visitedPoints[-3][1]:
            if targetY < posY and not self.isPointInObstacle((posX, posY-1)):
              posY -= 1
            elif targetY > posY and not self.isPointInObstacle((posX, posY+1)):
              posY += 1
            else:
              posX += 1
          else:
            posX += 1
        elif self.isPointInObstacle((posX+1, posY)) and \
            not self.isPointInObstacle((posX, posY + 1)) and \
            not self.isPointInObstacle((posX, posY - 1)):
          # get Y middle of nearest obstacle as target
          targetY = self.determineTarget((posX+1, posY))

          # get shortest route to move further
          posX, posY, subVisitedList = self.getShortestRoute((posX, posY))
          visitedPoints.extend(subVisitedList)
        elif self.isPointInObstacle((posX+1, posY)) and \
            not self.isPointInObstacle((posX, posY + 1)):
          # only up path available
          posY += 1
        elif self.isPointInObstacle((posX+1, posY)) and \
            not self.isPointInObstacle((posX, posY - 1)):
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

    
    p = np.zeros((ny, nx)) # np.add(np.absolute(u), np.absolute(v))
    p = np.add(np.absolute(u), np.absolute(v))
    # p = u
    # u[u == 1] = 0

    return X, Y, u, v, p


  # Calculate side array ---------------------------------------------------------------
  def getFlowPathSideArray(self):
    nx = int(self.xSize * self.densPerMeter) + 1 # number of points in grid
    ny = int(self.ySize * self.densPerMeter) + 1

    x = np.linspace(0,self.xSize,nx) # last point included, so exactly nx points
    y = np.linspace(0,self.ySize,ny) # last point included, so exactly ny points
    X,Y = np.meshgrid(x,y)    # makes 2-dimensional mesh grid

    v = np.zeros((ny, nx))
    u = np.zeros((ny, nx))  # for u-velocity I initialise to 1 everywhere

    
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
        if not self.isPointInObstacle((posX+1,posY)):
          # if point x+1 is not obstacle go right
          if len(visitedPoints) > 1 and targetY >= 0 and targetY != posY and \
              visitedPoints[-1][1] == visitedPoints[-2][1] and \
              visitedPoints[-1][1] == visitedPoints[-3][1]:
            if targetY < posY and not self.isPointInObstacle((posX, posY-1)):
              posY -= 1
            elif targetY > posY and not self.isPointInObstacle((posX, posY+1)):
              posY += 1
            else:
              posX += 1
          else:
            posX += 1
        elif self.isPointInObstacle((posX+1, posY)) and \
            not self.isPointInObstacle((posX, posY + 1)) and \
            not self.isPointInObstacle((posX, posY - 1)):
          # get Y middle of nearest obstacle as target
          targetY = self.determineTarget((posX+1, posY))

          # get shortest route to move further
          posX, posY, subVisitedList = self.getShortestRoute(
            (posX, posY), isSideArray=True)
          visitedPoints.extend(subVisitedList)
        elif self.isPointInObstacle((posX+1, posY)) and \
            not self.isPointInObstacle((posX, posY + 1)):
          # only up path available
          posY += 1
        elif self.isPointInObstacle((posX+1, posY)) and \
            not self.isPointInObstacle((posX, posY - 1)):
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

    
    p = np.zeros((ny, nx)) # np.add(np.absolute(u), np.absolute(v))
    p = np.add(np.absolute(u), np.absolute(v))
    # p = u
    # u[u == 1] = 0

    return X, Y, u, v, p