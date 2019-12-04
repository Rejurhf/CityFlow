import osmium

class OSMReader(osmium.SimpleHandler):
  def __init__(self):
    osmium.SimpleHandler.__init__(self)
    self.nodeList = []
    self.buildingList = []

  def addToBuildingList(self, elem, elem_type):
    elemId = elem.id
    # Visibility
    if elem.visible is None:
      visible = True
    else:
      visible = elem.visible
    # Name
    if elem.tags.get("addr:street") is None and elem.tags.get("addr:housenumber") is None:
      name = "Unknown"
    elif elem.tags.get("addr:street") is None:
      name = elem.tags.get("addr:housenumber")
    elif elem.tags.get("addr:housenumber") is None:
      name = elem.tags.get("addr:street")
    else:
      name = elem.tags.get("addr:street") + " " + elem.tags.get("addr:housenumber")
    # Building levels
    if elem.tags.get("building:levels") is None:
      building_levels = 2
    else:
      building_levels = elem.tags.get("building:levels")
    # Roof
    if elem.tags.get("roof:shape") is None:
      roof = "flat"
    else:
      roof = elem.tags.get("roof:shape")
    # Roof levels
    if elem.tags.get("roof:levels") is None:
      roof_levels = 1
    else:
      roof_levels = elem.tags.get("roof:levels")
    
    tmpDict ={
      "id": elemId,
      "visible": visible,
      "name": name,
      "building_levels": building_levels,
      "roof": roof,
      "roof_levels": roof_levels,
      "nodes": [node.ref for node in elem.nodes],
    }
    self.buildingList.append(tmpDict)

  def addToNodeList(self, elem, elem_type):
    tmpDict ={
      "id": elem.id,
      "visible": elem.visible,
      "lat": elem.location.lat,
      "lon": elem.location.lon,
    }
    self.nodeList.append(tmpDict)

  def node(self, n):
    self.addToNodeList(n, "node")

  def way(self, w):
    if "building" in w.tags:
      self.addToBuildingList(w, "way")
