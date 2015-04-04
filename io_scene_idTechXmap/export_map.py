## this file is GPL v3
## based partly on Campbell Barton's "export quake map" script
## Biel Bestué de Luna

import bpy
import mathutils

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
        #file.write('// brush "%s", "%s"\n' % (obj.name, obj.data.name))
        file.write('// brush "%s"\n' % (obj.name))
        file.write('{\n')
        file.write('brushDef3\n{\n')
        omesh = obj.to_mesh(scene, True, 'PREVIEW')
        omesh.update(calc_tessface=True)
        for face in omesh.polygons:
            normal = face.normal
            dist = mathutils.geometry.distance_point_to_plane(WorldOrigin, (obj.matrix_world * obj.data.vertices[face.vertices[0]].co), normal) #this is lossy due floating point precision loss
            file.write('( %.16f %.16f %.16f %.16f ) ' % (normal[0], normal[1], normal[2], dist))
            file.write(' ( ( 0.00390625 0 0 ) ( 0 0.00390625 0 ) )') #TODO
            file.write(' "textures/7318/concrete_01"') #TODO
            file.write(' 0 0 0\n') #TOUNDERSTANDWHATTHEHELLDOESITDO
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
