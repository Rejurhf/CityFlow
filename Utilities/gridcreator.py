from utilities import osmreader
import xml.etree.ElementTree as et
from geopy.distance import geodesic

class GridCreator:
  def __init__(self, osmFileName):
    self.osmFileName = osmFileName
    self.buildingList = []
    self.xSize = 0
    self.ySize = 0
    self.zSize = 0
    self.minLat = 0
    self.minLon = 0

  
  # main function ----------------------------------------------------------------------------------
  def getGridElements(self):
    # Get data from OSMgi
    osm = osmreader.OSMReader() # Declare OSMReader
    osm.apply_file(self.osmFileName)  # Connect to osm file

    # Get list of buildings and nodes
    buildings = osm.buildingList
    nodes = osm.nodeList
    
    # Find boundaries and starting points
    self.getAreaSizeFromOSM()

    # Add buildings wit coordinates to building list
    self.fillBuildingsData(buildings, nodes)

    return self.xSize, self.ySize, self.zSize, self.buildingList


  # Fill building List -----------------------------------------------------------------------------
  def fillBuildingsData(self, buildings, nodes):
    for building in buildings:
      # Create list of coordinates
      coorList = []
      for coor in building["nodes"]:
        osmNode = next(item for item in nodes if item["id"] == coor)

        xCoor, yCoor = self.getXYCoordinates(osmNode["lat"], osmNode["lon"])
        coorList.append((xCoor, yCoor))
      
      # Create tmp dict of building
      tmpDict = {
        "name": building["name"],
        "height": int(building["building_levels"]) * 3,
        "coordinates": coorList
      }
      
      # update ySize
      if (int(building["building_levels"]) * 3) > (self.zSize - 10):
        self.zSize = (int(building["building_levels"]) * 3) + 30

      # Append building list with new building
      self.buildingList.append(tmpDict)
      

  # Convert lat and lon to x, y on grid
  def getXYCoordinates(self, lat, lon):
    x = int(geodesic((0, self.minlon), (0, lon)).meters)
    y = int(geodesic((self.minlat, 0), (lat, 0)).meters)

    return x, y 


  # get lat amd lon boundaries from OSM ------------------------------------------------------------
  def findBoundaries(self):
    # create tree and root
    tree = et.parse(self.osmFileName)
    root = tree.getroot()

    # get boundaries
    self.minlat = root[0].get("minlat")
    maxlat = root[0].get("maxlat")
    self.minlon = root[0].get("minlon")
    maxlon = root[0].get("maxlon")

    return maxlat, maxlon
    

  # get area from OSM size in metres ---------------------------------------------------------------
  def getAreaSizeFromOSM(self):
    maxlat, maxlon = self.findBoundaries()

    self.xSize = int(geodesic((0, self.minlon), (0, maxlon)).meters)
    self.ySize = int(geodesic((self.minlat, 0), (maxlat, 0)).meters)


  def buildingListSize(self):
    return len(self.buildingList)