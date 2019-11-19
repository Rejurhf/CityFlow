from Utilities import visualize, rays2dcalculator

print("Calculate Top Rays")
xSize = 20  # nuberic size of in eg metres
ySize = 10
densPerMeter = 2.5 # points density per 1 meter

# Draw in xSize, ySize [left, width, bottom, height]
obstacles = [[5,1.5,4.1,3.9], [9.9, 2, 4.2, 2]]

topView = rays2dcalculator.Rays2dCalculator(xSize, ySize, densPerMeter, obstacles)
X, Y, u, v, p = topView.getFlowPathTopArray()

visualize.showPlot(X, Y, u, v, p, obstacles, "Test")
print("Top Rays Done")