from utilities import airflow2

print("C:", "Start")

# Simulation constants
xSize = 80
ySize = 45
zSize = 20
densPerMeter = 1

buildingDict = {'name': 'Single', 
  'height': 10, 
  'coordinates': [(27, 30), (27, 15), (18, 15), (18, 30), (27, 30)]
}
obstacleList = []
obstacleList.append(buildingDict)
print("C:", "xSize: {}, ySize: {}, zSize: {}".format(xSize, ySize, zSize))
print("C:", "Density per meter:", densPerMeter)
print("C:", "Buildings: {}".format(len(obstacleList)))

# Flow init
print("C:", "Init flow")
flow = airflow2.AirFlow2(xSize, ySize, zSize, densPerMeter, obstacleList)


# Make simulation
print("C:", "Start simulation")
flow.calculateFlow()



# # Get top view for 2m above ground
print("C:", "Show Top View")
flow.getTopViewLayerForMeter(2)

# # Get side view for 10m from left
print("C:", "Show Side View")
# flow.getSideViewLayerForMeter(23)