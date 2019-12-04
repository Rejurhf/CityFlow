import bpy
import bmesh
import json
import math
import mathutils
from mathutils import Vector

# Open buildings file
with open("D:\\Documents\\Studia\\Inzynierka\\CityFlow\\blender\\rays_191204T055656.txt") as inFile:
    rayList = json.load(inFile)

# Create new collection
rayCollection = bpy.data.collections.new(name="Rays")
# Add collection to scene
bpy.context.scene.collection.children.link(rayCollection)


for ray in rayList:
    name = ray["name"]
    startX = ray["x"]
    startY = ray["y"]
    startZ = ray["z"]
    multiplayer = ray["layerpermeter"]
    positions = ray["positions"]
    
    # Make a new BMesh
    bm = bmesh.new()

    # Add a circle XXX, should return all geometry created, not just verts.
    segmentsNumber = 8   
    bmesh.ops.create_circle(
        bm,
        cap_ends=False,
        radius=0.5,
        segments=segmentsNumber)

    # Rotate
    bmesh.ops.rotate(bm, 
        verts=bm.verts, 
        cent=(0.0, 0.0, 0.0), 
        matrix=mathutils.Matrix.Rotation(math.radians(90.0), 3, 'Y'))

    # Move circle
    bmesh.ops.translate(bm,
        verts=bm.verts,
        vec=(startX*multiplayer,startY*multiplayer,startZ*multiplayer))

    # Make translations   
    flagSkipFirst = True
    prevPos = [0,0,0]
    faceNumber = 0
    
    # Generate bottom mesh
    bottom = bm.faces.new(bm.verts)
    
    # Start translations
    for curPos in positions:
        if flagSkipFirst:
            flagSkipFirst = False
            prevPos = curPos
            continue

        bm.faces.ensure_lookup_table()
        face = [bm.faces[faceNumber]]

        newFace = bmesh.ops.extrude_face_region(bm, geom=face)

        # Calculate translation vector       
        x = (curPos[0] - prevPos[0]) * multiplayer
        y = (curPos[1] - prevPos[1]) * multiplayer
        z = (curPos[2] - prevPos[2]) * multiplayer
        
        # reassign position
        prevPos = curPos       
        
        bmesh.ops.translate(bm, 
            vec=Vector((x,y,z)), 
            verts=[v for v in newFace["geom"] if isinstance(v,bmesh.types.BMVert)])
            
        if faceNumber == 0:
            faceNumber = 1
        else:
            faceNumber += (segmentsNumber + 1)

    bm.normal_update()

    # Finish up, write the bmesh into a new mesh
    me = bpy.data.meshes.new("Mesh")
    bm.to_mesh(me)
    bm.free()

    # Add the mesh to the scene
    obj = bpy.data.objects.new(name, me)
    
    # Add to ray collection   
    obj.instance_collection = rayCollection
    rayCollection.objects.link(obj)
#    bpy.context.collection.objects.link(obj)
