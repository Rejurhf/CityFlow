import json
from utilities import airflow2, gridcreator, filewriter
import sys


def runSimulation(config):
  # Initialize grid creator
  try:
    gridCreator = gridcreator.GridCreator(config["osmmap"])
  except KeyError:
    print("[Err]", "osmap is not in config")
    return

  # Get grid elements
  try:
    xSize, ySize, zSize, obstacleList = gridCreator.getGridElements()
  except RuntimeError:
    print("[Err]", "Can not find OSM file ({})".format(config["osmmap"]))
    return

  if "raydenspermeter" not in config or config["raydenspermeter"] <= 0:
    densPerMeter = round(40/ySize, 2)
  else:
    densPerMeter = config["raydenspermeter"]

  # Print info
  printInfo(xSize, ySize, zSize, densPerMeter, obstacleList)

  # Get flow
  flow = getFlow(xSize, ySize, zSize, densPerMeter, obstacleList)

  # Display 2D visualizations
  visualize2D(config, flow, ySize, zSize)

  # Save data to files
  saveToFiles(config, flow, obstacleList)


def runCompare(config, map="cube"):
  print("[I]", "Compare mode")

  # Simulation constants
  xSize = 80
  ySize = 45
  zSize = 20
  if "raydenspermeter" not in config or config["raydenspermeter"] <= 0:
    densPerMeter = round(40/ySize, 2)
  else:
    densPerMeter = config["raydenspermeter"]

  # Build obstacle list
  obstacleList = []
  if map == "cube":
    buildingDict = {'name': 'Cube', 
      'height': 10, 
      'coordinates': [(27, 27), (27, 18), (18, 18), (18, 27), (27, 27)]
    }
    obstacleList.append(buildingDict)
  elif map == "cubeRow":
    buildingDict = {'name': 'Cube_2inRow_1', 
      'height': 10, 
      'coordinates': [(27, 27), (27, 18), (18, 18), (18, 27), (27, 27)]
    }
    obstacleList.append(buildingDict)
    buildingDict = {'name': 'Cube_2inRow_2', 
      'height': 10, 
      'coordinates': [(47, 27), (47, 18), (38, 18), (38, 27), (47, 27)]
    }
    obstacleList.append(buildingDict)
  elif map == "cubeCol":
    buildingDict = {'name': 'Cube_2inCol_1', 
      'height': 10, 
      'coordinates': [(27, 21), (27, 13), (18, 13), (18, 21), (27, 21)]
    }
    obstacleList.append(buildingDict)
    buildingDict = {'name': 'Cube_2inCol_2', 
      'height': 10, 
      'coordinates': [(27, 35), (27, 27), (18, 27), (18, 35), (27, 35)]
    }
    obstacleList.append(buildingDict)
  elif map == "cylinder":
    buildingDict = {'name': 'Cylinder', 
      'height': 10, 
      'coordinates': [(23,19), (22,19), (22,17), (21,17), (21,16), (19,16), (19, 15), (16,15), (16, 16),
        (14,16), (14,17), (13,17), (13,19), (12,19), (12,22), (13,22), (13,24), (14,24), (14,25),
        (16,25), (16,26), (19,26), (19,25), (21,25), (21,24), (22,24), (22,22), (23,22), (23,19)]
    }
    obstacleList.append(buildingDict)
  else:
    print("[Err]", "Unknown error")

  # Print info
  printInfo(xSize, ySize, zSize, densPerMeter, obstacleList)

  # Get flow
  flow = getFlow(xSize, ySize, zSize, densPerMeter, obstacleList)

  # Display 2D visualizations
  visualize2D(config, flow, ySize, zSize)

  # Save data to files
  saveToFiles(config, flow, obstacleList)


def printInfo(xSize, ySize, zSize, densPerMeter, obstacleList):
  print("[I]", "xSize: {}, ySize: {}, zSize: {}".format(xSize, ySize, zSize))
  print("[I]", "Density per meter:", densPerMeter)
  print("[I]", "Buildings: {}".format(len(obstacleList)))

def getFlow(xSize, ySize, zSize, densPerMeter, obstacleList):
  # Flow init
  print("[I]", "Init flow")
  flow = airflow2.AirFlow2(xSize, ySize, zSize, densPerMeter, obstacleList)

  # Make simulation
  print("[I]", "Start simulation")
  flow.calculateFlow()

  return flow

def visualize2D(config, flow, ySize, zSize):
  # 2D visualization
  if "visualize" in config and config["visualize"]:
    print("[I]", "Show 2D View")

    for viewStr in config["visualize"]:
      if viewStr[:3] == "top":
        # Show Top view
        try:
          layerNumber = int(viewStr[3:])
          if layerNumber >= 0 and layerNumber <= zSize:
            flow.getTopViewLayerForMeter(layerNumber)
          else:
            print("[Err]", "There is no layer:", viewStr)
        except ValueError:
          print("[Err]", "In \"{}\", \"{}\" must be Integer".format(viewStr, viewStr[3:]))
      elif viewStr[:4] == "side":
        # Show Side view
        try:
          layerNumber = int(viewStr[4:])
          if layerNumber >= 0 and layerNumber <= ySize:
            flow.getSideViewLayerForMeter(layerNumber)
          else:
            print("[Err]", "There is no layer:", viewStr)
        except ValueError:
          print("[Err]", "In \"{}\", \"{}\" must be Integer".format(viewStr, viewStr[4:]))
      else:
        print("[Err]", "Can not resolve \"{}\"".format(viewStr))

def saveToFiles(config, flow, obstacleList):
  # Save buildings array to file
  if "savebuildings" in config and config["savebuildings"] == "True":
    if "outbuildingname" in config:
      filewriter.writeToJSON(obstacleList, config["outbuildingname"])
    else:
      filewriter.writeToJSON(obstacleList, "buildings")

  # Save rays array to file
  if "saverays" in config and config["saverays"] == "True":
    if "withoutstraightrays" in config and config["withoutstraightrays"] == "True":
      withoutStraightRays = True
    else:
      withoutStraightRays = False
    if "everynray" in config and float(config["everynray"]).is_integer():
      everyNRay = config["everynray"]
    else:
      everyNRay = 1
    if "outrayname" in config:
      name = config["outrayname"]
    else:
      name = "ray"
    filewriter.writeToJSON(flow.getRayFlowList(
      withoutStraightRays=withoutStraightRays, everyNRay=everyNRay), name)

# Main ----------------------------------------------------------------------------------
print("[I]", "Start")

if len(sys.argv) > 1:
  fileName = sys.argv[1]
else:
  fileName = "config.txt"

# Open buildings file
print("[I]", "Open config file")
try:
  # Open config
  with open(fileName) as inFile:
    config = json.load(inFile)

  # Check map
  try:
    map = config["osmmap"]
  except KeyError:
    raise KeyError("Error")

  # If map is one of test cases, do test case
  if map in ["cube", "cubeRow", "cubeCol", "cylinder"]:
    runCompare(config, map=map)
  else:
    runSimulation(config)
except FileNotFoundError:
  print("[Err]", "Can not find config file ({})".format(fileName))
except KeyError:
  print("[Err]", "osmap is not in config")

print("[I]", "Finished")