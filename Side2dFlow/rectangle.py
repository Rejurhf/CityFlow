import calculateSideRays as sideRays
from Utilities import visualize

print("Calculate Side Rays")

xSize = 20  # nuberic size of in eg metres
ySize = 10
densPerMeter = 2.5 # points density per 1 meter

# Draw in xSize, ySize [left, width, bottom, height]
obstacles = [[5, 3, 0, 5]]

X, Y, u, v, p = sideRays.getFlowPathSideArrays(xSize, ySize, densPerMeter, obstacles)

visualize.showPlot(X, Y, u, v, p, obstacles, "Side")
print("Side Rays Done")