from utilities import visualize, rays2dcalculator

print("Calculate Side Rays")

xSize = 20  # nuberic size of in eg metres
ySize = 10
densPerMeter = 2.5 # points density per 1 meter

# Draw in xSize, ySize [left, width, bottom, height]
obstacles = [[6, 3, 0, 3], [12, 3, 0, 3]]

sideView = rays2dcalculator.Rays2dCalculator(xSize, ySize, densPerMeter, obstacles)
X, Y, u, v, p = sideView.getFlowPathSideArray()

visualize.showPlot(X, Y, u, v, p, obstacles, "Side")
print("Side Rays Done")