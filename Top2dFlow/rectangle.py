
import calculateRays as calculateRays
from Utilities import visualize


xSize = 20  # nuberic size of in eg metres
ySize = 10
densPerMeter = 2.5 # points density per 1 meter

# Draw in xSize, ySize [left, width, bottom, height]
obstacles = [[5,1.5,4.1,3.9], [13, 2, 2.6, 2]]

X, Y, u, v, p = calculateRays.getFlowPathTopArrays(xSize, ySize, densPerMeter, 
    obstacles)



# # u, v = self.getFlowPath(u, v, xSize, ySize, obstacle)
# # u, v = self.calcInObstacleFlow(u, v, xSize, ySize, obstacle)
# # u, v = self.calcUDecrease(u, v, xSize, ySize, obstacle)


# showPlot(X, Y, u, v, p, obstacle, "Title")

visualize.showPlot(X, Y, u, v, p, obstacles, "Test")
print("Done")