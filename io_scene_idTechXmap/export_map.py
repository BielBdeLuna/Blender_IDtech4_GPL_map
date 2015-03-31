## this file is GPL v3
## based partly on Campbell Barton's "export quake map" script
## Biel Bestué de Luna

import bpy
import mathutils
#import math

def get_eucleidan_distance(poly):
    """TODO"""
    return dist

def get_surface_equation(poly):
    normal = poly.normal
    dist = get_eucleidan_distance (poly)
    equation = normal.x, normal.y, normal.z, dist
    return equation

"""
 mathutils.geometry.intersect_line_plane(line_a, line_b, plane_co, plane_no, no_flip=False)

    Calculate the intersection between a line (as 2 vectors) and a plane. Returns a vector for the intersection or None.
    Parameters:	

        line_a (mathutils.Vector) – First point of the first line
        line_b (mathutils.Vector) – Second point of the first line
        plane_co (mathutils.Vector) – A point on the plane
        plane_no (mathutils.Vector) – The direction the plane is facing

    Returns:	

    The point of intersection or None when not found
    Return type:	

    mathutils.Vector or None
"""

def export_map(context, filepath):
    
    file = open(filepath, 'w')

    scene = context.scene
    objects = context.selected_objects

    ol_mesh = []
    ol_surf = []

    for o in objects:
        if o.type is 'MESH':
            ol_mesh.append(o)
        if o.type is 'SURFACE':
            ol_surf.append(o)

    if ol_mesh or ol_surf:
        # brushes and surf's must be under worldspan
        file.write('Version 2\n// entity 0\n')
        file.write('{\n')
        file.write('"classname" "worldspawn"\n')

    for o in ol_mesh:
        file.write('// brush "%s", "%s"\n' % (o.name, o.data.name))
        file.write('{\n')
        omesh = o.to_mesh(scene, True, 'PREVIEW')
        #omesh.update(calc_tessface=True)
        for p in omesh.polygons
            normal = p.normal
            dist = 1 #TODO
            file.write('brushDef3\n{\n')
            file.write('( %.16f %.16f %.16f %.16f ) ' % (normal[0], normal[1], normal[2], dist))
            file.write(' ( ( 0.00390625 0 0 ) ( 0 0.00390625 0 ) )')
            file.write(' "textures/7318/concrete_01"')
            file.write(' 0 0 0\n')
            file.write('}\n') #end of "brushDef3" function
        file.write('}\n') #end of brush "o"
    #for o in ol_surf:
        #TODO

    if ol_mesh or ol_surf:
        file.write('}\n') #worldspawn end

    #outside the worldspawn entity it's the place for the other entities


    file.close()

def save(operator,
         context,
         filepath=None,
         global_scale=100.0,
         face_thickness=0.1,
         texture_null="NULL",
         texture_opts='0 0 0 1 1 0 0 0',
         grid_snap=False,
         ):

    global PREF_SCALE
    global PREF_FACE_THICK
    global PREF_NULL_TEX
    global PREF_DEF_TEX_OPTS
    global PREF_GRID_SNAP

    PREF_SCALE = global_scale
    PREF_FACE_THICK = face_thickness
    PREF_NULL_TEX = texture_null
    PREF_DEF_TEX_OPTS = texture_opts
    PREF_GRID_SNAP = grid_snap

    export_map(context, filepath)

    return {'FINISHED'}

"""
import bpy  
      
current_obj = bpy.context.active_object  
      
print("="*40) # printing marker  
for polygon in current_obj.data.polygons:
    verts_in_face = polygon.vertices[:]  
    print("face index", polygon.index)  
    print("normal", polygon.normal)  
    for vert in verts_in_face:  
        print("vert", vert, " vert co", current_obj.data.vertices[vert].co)  
"""
class export_brushes(bpy.types.Operator, ExportHelper):
    """export your cubes to idtech3/idtech4 brushes"""
    """
    - make a list of selected objects in the scene
        - if there aren't selected obejcts in the scene gather them all in the list
    - check if all their faces are coplanar?
        - error if non complanar faces?
    - for every object
        - for every coplanar quad face
            - gather normal
            - find the shortest distance between the surface, in which the face is inscribed in, and the global centre
            - figure out how to translate the UVmap to a global UV mapping
            - write brush info in the *.map file
        - get a solution for non coplanar quad faces?
            - separate the two tris as if they where two different surfaces?
                - i think non coplanar quad faces are not allowed in radiant
            - are concave/convex surfaces a problem?
    """

class export_entities
    """export your cubes to idtech3/idtech4 entities"""

class export_patches
    """export your surfaces to idtech3/idtech4 patches"""
