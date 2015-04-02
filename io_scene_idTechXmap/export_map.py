## this file is GPL v3
## based partly on Campbell Barton's "export quake map" script
## Biel Bestué de Luna

import bpy
import mathutils
#import math
    
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

     mathutils.geometry.distance_point_to_plane(pt, plane_co, plane_no)

    Returns the signed distance between a point and a plane (negative when below the normal).
    Parameters:	

        pt (mathutils.Vector) – Point
        plane_co (mathutils.Vector) – First point of the quad
        plane_no (mathutils.Vector) – Second point of the quad

    Return type:	

    float
"""

def export_map(context, filepath):    
    import time

    t = time.time()
    WorldOrigin = mathutils.Vector((0.0,0.0,0.0))  

    print("opening file")
    file = open(filepath, 'w')

    scene = context.scene
    objects = context.selected_objects

    print("create list for exporting elements")
    l_meshes = []
    l_surfes = []

    for obj in objects:
        if obj.type == 'MESH':
            l_meshes.append(obj)
        elif obj.type == 'SURFACE':
            l_surfes.append(obj)

    if l_meshes or l_surfes:
        # brushes and surf's must be under worldspan
        print("since there are brushes or surfaces let's create a worldspawn entity")
        file.write('Version 2\n// entity 0\n')
        file.write('{\n')
        file.write('"classname" "worldspawn"\n')

    print("starting with brushes")
    for obj in l_meshes:
        file.write('// brush "%s", "%s"\n' % (obj.name, obj.data.name))
        file.write('{\n')
        file.write('brushDef3\n{\n')
        omesh = obj.to_mesh(scene, True, 'PREVIEW')
        omesh.update(calc_tessface=True)
        for face in omesh.polygons:
            normal = face.normal
            """
            if WorldOrigin == normal: #this is a potential gamebreaker
                point2 = normal*2
            else:
                point2 = normal
   
            #vert = face.vertices[0]
            #intersect = mathutils.geometry.intersect_line_plane(WorldOrigin, normal, vert, normal, no_flip=False)
            intersect = mathutils.geometry.intersect_line_plane(WorldOrigin, point2, face.vertices[0], normal, False)
            #deltaWoI = intersect - WorldOrigin            
            dist = (intersect - WorldOrigin).lenght
            """
            dist = mathutils.geometry.distance_point_to_plane(WorldOrigin, face.vertices[0], normal)
            file.write('( %.16f %.16f %.16f %.16f ) ' % (normal[0], normal[1], normal[2], dist))
            file.write(' ( ( 0.00390625 0 0 ) ( 0 0.00390625 0 ) )')
            file.write(' "textures/7318/concrete_01"')
            file.write(' 0 0 0\n')
        file.write('}\n') #end of "brushDef3" function
        file.write('}\n') #end of brush "o"
    #for obj in l_surfes:
        #TODO

    if l_meshes or l_surfes:
        print("starting with surfaces")

    file.write('}\n') #worldspawn end

    #outside the worldspawn entity it's the place for the other entities

    print("closing file")
    file.close()

    print("Exported Map in %.4fsec" % (time.time() - t))

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
