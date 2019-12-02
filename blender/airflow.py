import bpy
import bmesh
import math
import mathutils
from mathutils import Vector

# Make a new BMesh
bm = bmesh.new()

# Add a circle XXX, should return all geometry created, not just verts.
bmesh.ops.create_circle(
    bm,
    cap_ends=False,
    radius=0.2,
    segments=8)

# Rotate
bmesh.ops.rotate(bm, 
    verts=bm.verts, 
    cent=(0.0, 0.0, 0.0), 
    matrix=mathutils.Matrix.Rotation(math.radians(90.0), 3, 'Y'))

# Generate bottom mesh
bottom = bm.faces.new(bm.verts)
# Stretch figure to top mesh
top = bmesh.ops.extrude_face_region(bm, geom=[bottom])

bmesh.ops.translate(bm, vec=Vector((1,0,0)), verts=[v for v in top["geom"] if isinstance(v,bmesh.types.BMVert)])

#bm.normal_update()
bm.faces.ensure_lookup_table()
face = [bm.faces[1]]

top1 = bmesh.ops.extrude_face_region(bm, geom=face)

bmesh.ops.translate(bm, vec=Vector((1,1,0)), verts=[v for v in top1["geom"] if isinstance(v,bmesh.types.BMVert)])

bm.faces.ensure_lookup_table()
face = [bm.faces[10]]
top2 = bmesh.ops.extrude_face_region(bm, geom=face)

bmesh.ops.translate(bm, vec=Vector((1,1,1)), verts=[v for v in top2["geom"] if isinstance(v,bmesh.types.BMVert)])


bm.faces.ensure_lookup_table()
face = [bm.faces[19]]
top3 = bmesh.ops.extrude_face_region(bm, geom=face)

bmesh.ops.translate(bm, vec=Vector((1,0,1)), verts=[v for v in top3["geom"] if isinstance(v,bmesh.types.BMVert)])


bm.normal_update()

# Finish up, write the bmesh into a new mesh
me = bpy.data.meshes.new("Mesh")
bm.to_mesh(me)
bm.free()


# Add the mesh to the scene
obj = bpy.data.objects.new("Object", me)
bpy.context.collection.objects.link(obj)

# Select and make active
bpy.context.view_layer.objects.active = obj
obj.select_set(True)