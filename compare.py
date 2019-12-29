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
# buildingDict = {'name': 'Single', 
#   'height': 10, 
#   'coordinates': [(23,19), (22,19), (22,17), (21,17), (21,16), (19,16), (19, 15), (16,15), (16, 16),
#     (14,16), (14,17), (13,17), (13,19), (12,19), (12,22), (13,22), (13,24), (14,24), (14,25),
#     (16,25), (16,26), (19,26), (19,25), (21,25), (21,24), (22,24), (22,22), (23,22), (23,19)]
# }
# buildingDict = {'name': 'Single', 
#   'height': 10, 
#   'coordinates': [(30,25), (10,25), (10,20), (20,20), (20,15), (10,15), (10,10), (30,10), (30,25)]
# }
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
print(obstacleList)

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
flow.getSideViewLayerForMeter(23)