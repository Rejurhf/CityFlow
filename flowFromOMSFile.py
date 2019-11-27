from utilities import airflow, gridcreator

print("FFOMS:", "Read OSM file")

# initialize grid creator
gridCreator = gridcreator.GridCreator("resources/map2.osm")

# get grid elements
xSize, ySize, zSize, obstacleList = gridCreator.getGridElements()
densPerMeter = 0.5

print("FFOMS:", "xSize: {}, ySize: {}, zSize: {}".format(xSize, ySize, zSize))
print("FFOMS:", "Density per meter:", densPerMeter)
print("FFOMS:", "Buildings: {}".format(gridCreator.buildingListSize()))

flow = airflow.AirFlow(xSize, ySize, zSize, densPerMeter, obstacleList)

# Make simulation
print("FFC:", "Start simulation")
flow.calculateFlow()

# Get top view for 2m above ground
print("FFC:", "Show Top View")
flow.getTopViewLayerForMeter(2)

# # Get side view for 10m from left
print("FFC:", "Show Side View")
flow.getSideViewLayerForMeter(30)

print("Simulation Done")


