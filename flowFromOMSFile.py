from utilities import gridcreator

print("FFOMS:", "Read OSM file")

gridCreator = gridcreator.GridCreator("resources/map2.osm")

xSize, ySize, zSize = gridCreator.getGridElements()

print("FFOMS:", "xSize: {}, ySize: {}, zSize: {}".format(xSize, ySize, zSize))
print("FFOMS:", "Buildings: {}".format(gridCreator.buildingListSize()))
