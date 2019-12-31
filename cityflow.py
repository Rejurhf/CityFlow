import json
from utilities import airflow2, gridcreator, filewriter


def runSimulation(config):
  # Initialize grid creator
  gridCreator = gridcreator.GridCreator(config["osmmap"])


  # Get grid elements
  try:
    xSize, ySize, zSize, obstacleList = gridCreator.getGridElements()
  except RuntimeError:
    print("[CF]", "Can not find OSM file ({})".format(config["osmmap"]))
    return

  if "raydenspermeter" not in config or config["raydenspermeter"] <= 0:
    densPerMeter = round(40/ySize, 2)
  else:
    densPerMeter = config["raydenspermeter"]

  print("[CF]", "xSize: {}, ySize: {}, zSize: {}".format(xSize, ySize, zSize))
  print("[CF]", "Density per meter:", densPerMeter)
  print("[CF]", "Buildings: {}".format(len(obstacleList)))


  # Flow init
  print("[CF]", "Init flow")
  flow = airflow2.AirFlow2(xSize, ySize, zSize, densPerMeter, obstacleList)

  # Make simulation
  print("[CF]", "Start simulation")
  flow.calculateFlow()


  # 2D visualization
  if "visualize" in config and config["visualize"]:
    print("[CF]", "Show 2D View")

    for viewStr in config["visualize"]:
      if viewStr[:3] == "top":
        # Show Top view
        try:
          layerNumber = int(viewStr[3:])
          if layerNumber >= 0 and layerNumber <= zSize:
            flow.getTopViewLayerForMeter(layerNumber)
          else:
            print("There is no layer:", viewStr)
        except ValueError:
          print("In \"{}\", \"{}\" must be Integer".format(viewStr, viewStr[3:]))
      elif viewStr[:4] == "side":
        # Show Side view
        try:
          layerNumber = int(viewStr[4:])
          if layerNumber >= 0 and layerNumber <= ySize:
            flow.getSideViewLayerForMeter(layerNumber)
          else:
            print("There is no layer:", viewStr)
        except ValueError:
          print("In \"{}\", \"{}\" must be Integer".format(viewStr, viewStr[4:]))
      else:
        print("Can not resolve \"{}\"".format(viewStr))


  # Save buildings array to file
  if "savebuildings" in config and config["savebuildings"] == "True":
    if "outbuildingname" in config:
      filewriter.writeToJSON(obstacleList, config["outbuildingname"])
    else:
      filewriter.writeToJSON(obstacleList, "buildings")

  # Save buildings array to file
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


# Main -----------------------------------------------------------------------
print("[CF]", "Start")

# Open buildings file
print("[CF]", "Open config file")
try:
  with open("config.txt") as inFile:
    config = json.load(inFile)

  runSimulation(config)
except FileNotFoundError:
  print("[CF]", "Can not find config file")

print("[CF]", "Finished")