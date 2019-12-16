from utilities import airflow2

print("C:", "Start")

# Simulation constants
xSize = 80
ySize = 45
zSize = 20
densPerMeter = 1

buildingDict = {'name': 'Single', 
  'height': 10, 
  'coordinates': [(27, 27), (27, 18), (18, 18), (18, 27), (27, 27)]
}
obstacleList = []
obstacleList.append(buildingDict)

# Flow init
print("C:", "Init flow")
flow = airflow2.AirFlow2(xSize, ySize, zSize, densPerMeter, obstacleList)


# Make simulation
print("C:", "Start simulation")
flow.calculateFlow()



# # Get top view for 2m above ground
print("FFC:", "Show Top View")
flow.getTopViewLayerForMeter(2)

# # Get side view for 10m from left
print("FFC:", "Show Side View")
flow.getSideViewLayerForMeter(23)