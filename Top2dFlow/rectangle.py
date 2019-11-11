import matplotlib.pyplot as plt
import numpy as np
import math as mth
import calculateRays as calculateRays
from Utility import visualize


def showPlot(X, Y, u, v, p, obstacle, titleText="no text"):
    # Plot the last figure on screen
    fig = plt.figure(figsize=(100, 50), dpi=25)
    plt.contourf(X, Y, p, alpha=0.5)  # alpha - background intensity
    plt.tick_params(axis='both', which='major', labelsize=80)
    cbar = plt.colorbar()
    cbar.ax.tick_params(labelsize=80)
    plt.contour(X, Y, p)
    M = np.hypot(u, v)
    plt.quiver(X, Y, u, v, M, scale=1 / 0.02)  ##plotting velocity
    # plt.scatter(X, Y, color='r')
    plt.broken_barh([(obstacle[0], obstacle[1])], (obstacle[2], obstacle[3]), facecolors='grey', alpha=0.8)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(titleText, fontsize=80)
    plt.show()



# nx = 51 # number of points in grid
# ny = 26
# xSize = 20  # nuberic size of in eg metres
# ySize = 10
# x = np.linspace(0,xSize,nx) # last point included, so exactly nx points
# y = np.linspace(0,ySize,ny) # last point included, so exactly ny points
# X,Y = np.meshgrid(x,y)       # makes 2-dimensional mesh grid

# # Draw in xSize, ySize [left, width, bottom, height]
# obstacle = [7,1.5,2.1,5.9]

# v = np.zeros((ny, nx))
# u = np.zeros((ny, nx))    # for u-velocity I initialise to 1 everywhere

# # u, v = self.getFlowPath(u, v, xSize, ySize, obstacle)
# # u, v = self.calcInObstacleFlow(u, v, xSize, ySize, obstacle)
# # u, v = self.calcUDecrease(u, v, xSize, ySize, obstacle)

# p = np.zeros((ny, nx)) # np.add(np.absolute(u), np.absolute(v))
# p = u
# # u[u == 1] = 0
# u[0,0] = 2.3
# showPlot(X, Y, u, v, p, obstacle, "Title")

calculateRays.testR()
visualize.testV()