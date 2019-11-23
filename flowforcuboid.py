from utilities import visualize, airflow

print("FFC:", "Start simulation")

xSize = 30  # nuberic size of in eg metres
ySize = 20
zSize = 10
densPerMeter = 2.5 # points density per 1 meter

# Draw in xSize, ySize, zSize [xStart, xDepth, yStart, yDepth, zStart, zDepth]
obstacleList = [[6, 3, 8, 4, 0, 4]]

# Create case object
testFlow = airflow.AirFlow(xSize, ySize, zSize, densPerMeter, obstacleList)

# Make simulation
print("FFC:", "Start simulation")
testFlow.calculateFlow()

# Get top view for 2m above ground
print("FFC:", "Show Top View")
testFlow.getTopViewLayerForMeter(2)

# Get side view for 10m from left
print("FFC:", "Show Side View")
testFlow.getSideViewLayerForMeter(10)