from utilities import airflow2

print("C:", "Start")

# Simulation constants
xSize = 80
ySize = 45
zSize = 20
densPerMeter = 1

firstX = 18
firstY = 13
depth = 9
secondY = 14

buildingDict = {'name': 'Single', 
  'height': 10, 
  'coordinates': [(firstX+depth, firstY+depth), (firstX+depth, firstY), 
    (firstX, firstY), (firstX, firstY+depth), (firstX+depth, firstY+depth)]
}

obstacleList = []
obstacleList.append(buildingDict)
buildingDict = {'name': 'Single', 
  'height': 10, 
  'coordinates': [(firstX+depth, firstY+depth+secondY), (firstX+depth, firstY+secondY), 
    (firstX, firstY+secondY), (firstX, firstY+depth+secondY), (firstX+depth, firstY+depth+secondY)]
}
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
flow.getTopViewLayerForMeter(1)


# # Get side view for 10m from left
print("C:", "Show Side View")
# flow.getSideViewLayerForMeter(23)