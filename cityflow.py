import json
from utilities import airflow2, gridcreator, filewriter

print("[CF]", "Start")

# Open buildings file
print("[CF]", "Open config file")
with open("config.txt") as inFile:
  config = json.load(inFile)

# Initialize grid creator
gridCreator = gridcreator.GridCreator(config["osmmap"])

# Get grid elements
xSize, ySize, zSize, obstacleList = gridCreator.getGridElements()
densPerMeter = config["raydenspermeter"]

print("[CF]", "xSize: {}, ySize: {}, zSize: {}".format(xSize, ySize, zSize))
print("[CF]", "Density per meter:", densPerMeter)
print("[CF]", "Buildings: {}".format(len(obstacleList)))
print(obstacleList)

# Flow init
print("[CF]", "Init flow")
flow = airflow2.AirFlow2(xSize, ySize, zSize, densPerMeter, obstacleList)

# Make simulation
print("[CF]", "Start simulation")
flow.calculateFlow()

# # Get top view for 2m above ground
print("[CF]", "Show Top View")
flow.getTopViewLayerForMeter(2)

# # Get side view for 10m from left
print("[CF]", "Show Side View")
flow.getSideViewLayerForMeter(23)