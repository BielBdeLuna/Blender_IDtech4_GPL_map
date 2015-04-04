## this file is GPL v3
## based partly on Campbell Barton's "export quake map" script
## Biel Bestué de Luna

import bpy
import mathutils

entity_num = 0;
brush_num = 0;
surf_num = 0;

def entity_export(scene):
    global entity_num

    file.write('{\n')
    if entity_num == 0:
        file.write('// entity %i\n' % (entity_num))
        entity_num = entity_num + 1
        file.write('"classname" "worldspawn"\n')        
    file.write('}\n')

def brushDef3_export(scene, l_brushes, file, scale):
    global brush_num

    WorldOrigin = mathutils.Vector((0.0,0.0,0.0))
    for obj in l_brushes:
        file.write('// brush "%s"\n' % (obj.name))
            #this is idTechX needed tokens
        file.write('{\n')
        file.write('brushDef3\n{\n')
        omesh = obj.to_mesh(scene, True, 'PREVIEW') #we might not need that
        #omesh.update(calc_tessface=True)
        for face in omesh.polygons:
                # the normal of the surface
            normal = face.normal
                # a vertex on the surface (that we know it's position) will help us define the surface
            vert = obj.data.vertices[face.vertices[0]].co
                # let's put that vertex in the world context, where it is?
            vert_world_pos = obj.matrix_world * vert
                # let's calc the minimum distance between the surface and the world origin (eucleidan distance?)
            dist = mathutils.geometry.distance_point_to_plane(WorldOrigin, vert_world_pos, normal)
                #let's scale that distance by the scale on the exporter
            dist_scaled = dist * scale

            file.write('( %.16f %.16f %.16f %.16f ) ' % (normal[0], normal[1], normal[2], dist_scaled))
                # TODO this is all idTechX needed tokens with false info
            file.write(' ( ( 0.00390625 0 0 ) ( 0 0.00390625 0 ) )') #TODO
            file.write(' "textures/7318/concrete_01"') #TODO
            file.write(' 0 0 0\n') #TOUNDERSTANDWHATTHEHELLDOESITDO
            brush_num = brush_num + 1
        file.write('}\n') #end of "brushDef3" function
        file.write('}\n') #end of brush "o"
"""
def patchDef2_export(scene, l_surfaces, file, scale):
    global surf_num
 
    for obj in l_surfaces:
        surf_num = surf_num + 1
        #TODO
"""

def export_map(context, filepath):    
    import time
    global entity_num
    global PREF_SCALE

    t = time.time()
    ExportScale = PREF_SCALE
    
    scene = context.scene

    print("opening file")
    file = open(filepath, 'w')

    print("create list for exporting elements")
    l_meshes = []
    l_surfes = []

    for obj in context.selected_objects:
        if obj.type == 'MESH':
            l_meshes.append(obj)
        elif obj.type == 'SURFACE':
            l_surfes.append(obj)

    if l_meshes or l_surfes:
            # brushes and surf's must be under worldspan entity
        print("since there are brushes or surfaces let's create a worldspawn entity")
        file.write('Version 2\n')
        file.write('// entity %i\n' % (entity_num))
        entity_num = entity_num + 1
        file.write('{\n')
        file.write('"classname" "worldspawn"\n')

    print("starting with brushes")
    brushDef3_export(scene, l_meshes, file, ExportScale)

    #print("starting with surfaces")
    #patchDef2_export(scene, l_surfes, file, ExportScale)

    #for obj in l_surfes:        
        #TODO

    if l_meshes or l_surfes:
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
