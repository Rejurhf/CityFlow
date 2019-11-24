import osmium

class OSMReader(osmium.SimpleHandler):
  def __init__(self):
    osmium.SimpleHandler.__init__(self)
    self.nodeList = []
    self.buildingList = []

  def addToBuildingList(self, elem, elem_type):
    tmpDict ={
      "id": elem.id,
      "visible": elem.visible,
      "name": elem.tags.get("addr:street") + " " + elem.tags.get("addr:housenumber"),
      "building_levels": elem.tags.get("building:levels"),
      "roof": elem.tags.get("roof:shape"),
      "roof_levels": elem.tags.get("roof:levels"),
      "nodes": list(set([node.ref for node in elem.nodes])),
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

  def relation(self, r):
    print("tak")

  def area(self, a):
    print("area")
    print(self)
    # print(a)

  def changeset(self, o):
    print("normalize")
