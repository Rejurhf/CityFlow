import bpy, json, bmesh
from math import *
from mathutils import Vector

# Open buildings file
with open("D:\\Documents\\Studia\\Inzynierka\\CityFlow\\blender\\buildings_191204T063637.txt") as inFile:
    buildingList = json.load(inFile)

# Create new collection
buildingCollection = bpy.data.collections.new(name="Buildings")
# Add collection to scene
bpy.context.scene.collection.children.link(buildingCollection)

for building in buildingList:
    coordinates = building["coordinates"]
    height = building["height"]
    name = building["name"]

    # Convert list of list to list of tuple buildings_191127T200825.txt
    verts = tuple([(x[0], x[1]) for x in coordinates])
    bm = bmesh.new()

    # Assign verts to mesh
    for v in verts:
        bm.verts.new((v[0], v[1], 0))

    # Generate bottom mesh
    bottom = bm.faces.new(bm.verts)
    # Stretch figure to top mesh
    top = bmesh.ops.extrude_face_region(bm, geom=[bottom])

    bmesh.ops.translate(bm, vec=Vector((0,0,height)), verts=[v for v in top["geom"] if isinstance(v,bmesh.types.BMVert)])

    bm.normal_update()

    # Generate a mesh and transfer data from bmesh object
    m = bpy.data.meshes.new(name)
    bm.to_mesh(m)

    # Create a new mesh object and link to scene
    o = bpy.data.objects.new(name, m)
    o.instance_collection = buildingCollection
#    bpy.data.collections["Buildings"].children.link(bpy.data.collections[name])
#    bpy.context.scene.collection.objects.link(o)
    buildingCollection.objects.link(o)
