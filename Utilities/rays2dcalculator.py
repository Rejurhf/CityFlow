import numpy as np
import math as mth
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class Rays2dCalculator:  
  def __init__(self, xSize, ySize, layerIndicator, densPerMeter, obstacleList, isTopView = True):
    # Max size of array in metres
    self.xSize = xSize
    self.ySize = ySize
    # Current layer of array top/side
    self.layerIndicator = layerIndicator
    # Point density per meter
    self.densPerMeter = densPerMeter
    # List of buildings
    self.obstacleList = obstacleList
    # Flag is top view
    self.isTopView = isTopView

  # Main function ---------------------------------------------------------------------------
  def getFlowPathArray(self):
    if self.isTopView:
      return self.getFlowPathTopArray()
    else:
      return self.getFlowPathSideArray()


  # Is point in obstacle check ---------------------------------------------------------
  def isPointInObstacle(self, point):
    for obstacle in self.obstacleList:
      # convert layer number to metres, create the point and polygon 
      tmpPoint = Point(point[0]/self.densPerMeter, point[1]/self.densPerMeter)
      polygon = Polygon(obstacle["coordinates"])

      # If in obstacle (check height) return True
      if self.isTopView and polygon.contains(tmpPoint) and \
          self.layerIndicator/self.densPerMeter <= obstacle["height"]:
        return True
      elif not self.isTopView and polygon.contains(tmpPoint):
        return True
    return False


  # Get shortest route for top array ---------------------------------------------------
  def getShortestRoute(self, pointPos):
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

    if not self.isTopView:
      return upPosX, upPosY, upVisitedList

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
      if downPosY < 0 and self.isTopView:
        return upPosX, upPosY, upVisitedList

    # get shorter route and return
    if len(downVisitedList) > len(upVisitedList):
      return upPosX, upPosY, upVisitedList
    else:
      return downPosX, downPosY, downVisitedList 


  # Determine target ray position ------------------------------------------------------
  def determineTarget(self, pointPos):
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

      while posX < nx and 0 <= posY < ny and (posX, posY) not in visitedPoints:
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

    # Comment this
    # v = np.zeros((ny, nx))
    # u = np.ones((ny, nx))  # for u-velocity I initialise to 1 everywhere

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
            (posX, posY))
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

    # Comment this
    # v = np.zeros((ny, nx))
    # u = np.ones((ny, nx))  # for u-velocity I initialise to 1 everywhere

    p = np.zeros((ny, nx)) # np.add(np.absolute(u), np.absolute(v))
    p = np.add(np.absolute(u), np.absolute(v))
    # p = u
    # u[u == 1] = 0

    return X, Y, u, v, p