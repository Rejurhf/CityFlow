from utilities import osmreader

print("FFOMS:", "Read OSM file")

osm = osmreader.OSMReader() # Declare OSMReader
osm.apply_file("resources/map2.osm")  # Connect to osm file

# print("Building list:\n", osm.buildingList)
# print("Node list:\n", osm.nodeList)
print("Nodes:", len(osm.nodeList), "Buildings:", len(osm.buildingList))