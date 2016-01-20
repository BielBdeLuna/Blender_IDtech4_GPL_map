## this file is GPL v3
## based partly on Campbell Barton's "export quake map" script
## Biel Bestué de Luna

import bpy
import mathutils
#import bl_processing

#processing
#present the input floats as either integers or floats depending on their true nature and also with a correct sign
def clean_floats(n):
    if n.is_integer():

        if False:
             #for those odd "-0" cases
            if n == -0:
                n = 0

        return "%s" % (n)
    else:
        return "%.8f" % (n)
"""
# The authors of this work have released all rights to it and placed it
# in the public domain under the Creative Commons CC0 1.0 waiver
# (http://creativecommons.org/publicdomain/zero/1.0/).
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# Retrieved from: http://en.literateprograms.org/Dot_product_(Python)?oldid=19485
def dot(vector1, vector2):
    return sum(map(lambda a, b: a * b, vector1, vector2)))
"""
#idTechX related
def hack_info_player_start():
    global l_entities

    ent_info_player_start = []
    key_val = ['classname', 'info_player_start']
    ent_info_player_start.append(key_val)
    key_val = ['name', 'info_player_start_1']
    ent_info_player_start.append(key_val)
    key_val = ['angle', '270']
    ent_info_player_start.append(key_val)
    key_val = ['origin', '0 0 32']
    ent_info_player_start.append(key_val)
    l_entities.append(ent_info_player_start)

def hack_light():
    global l_entities
    
    ent_spot_light = []
    key_val = ['classname', 'light']
    ent_spot_light.append(key_val)
    key_val = ['name', 'light_1']
    ent_spot_light.append(key_val)
    key_val = ['light_center', '0 0 0']
    ent_spot_light.append(key_val)
    key_val = ['light_radius', '600 600 600']
    ent_spot_light.append(key_val)
    key_val = ['origin', '0 0 96']
    ent_spot_light.append(key_val)
    l_entities.append(ent_spot_light)

def create_worldspawn():
    global l_entities
    global l_brushes
    global l_patches
    
    #we create a new entity, a list of key-val data tuples
    ent_worldspawn = []
    #first we input all the key-val data
    key_val = ['classname', 'worldspawn']
    ent_worldspawn.append(key_val)
    #then if there is any brush data we add it to the entity
    for obj in l_brushes: #not all entities are worldspawn entities
        #TODO add a check to see if that brush is owned by an entity different than worldspawn
        key_val = ['brush_data', obj]
        ent_worldspawn.append(key_val)
    for obj in l_patches:
        key_val = ['patch_data', obj]
        ent_worldspawn.append(key_val)
    #then we append the new entity withh all it's data in the list of entities
    l_entities.append(ent_worldspawn)

def brushDef3_export(scene, obj, file):
    global brush_num
    global PREF_SCALE
    global PREF_NULL_TEX
    
    WorldOrigin = mathutils.Vector((0.0,0.0,0.0))

    file.write('// brush %i : "%s"\n' % (brush_num, obj.name))
    brush_num += 1
    file.write('{\nbrushDef3\n{\n')
    omesh = obj.to_mesh(scene, True, 'PREVIEW') #we might not need that
    #omesh.update(calc_tessface=True)
    for face in omesh.polygons:
            #from every face of a brush we need:
            #the normal of the surface
            #a vertex on the surface (that we know it's position) will help us define the surface
            #put that vertex in the world context, where it is?
            #calculate the minimum distance between the surface and the world origin (eucleidan distance?)
            #scale that distance by the scale on the exporter
        normal = face.normal 
        vert = mathutils.Vector((0.0, 0.0, 0.0)) + obj.data.vertices[face.vertices[0]].co
        
        i = 0
        while( i <= 2 ):
            vert[i] = ( vert[i] + obj.location[i] ) * obj.scale[i]
            i += 1
        
        #vert = vert * obj.matrix_world
        dist = mathutils.geometry.distance_point_to_plane( mathutils.Vector((0.0,0.0,0.0)), vert, normal ) * PREF_SCALE
        clean_results = [ clean_floats(normal[0]), clean_floats(normal[1]), clean_floats(normal[2]), clean_floats(dist) ]
        file.write('( ' + clean_results[0] + ' ' + clean_results[1] + ' ' + clean_results[2] + ' ' + clean_results[3] + ' )')
            # TODO this is all idTechX needed tokens with false info
        file.write(' ( ( 0.03125 -0 -0 ) ( 0 0.03125 0 ) )') #TODO this is false info
        if len(obj.material_slots) == 0:
            mat_name = PREF_NULL_TEX
        else:
            mat_name = obj.material_slots[0].name
        file.write(' "%s" ' % (mat_name)) #TODO add the texture            
        file.write('0 0 0\n') #TOUNDERSTANDWHATTHEHELLDOESITDO
    file.write('}\n}\n') #end of "brushDef3" function

def patchDef2_export(scene, obj, file):
    import time
    global patch_num
    global PREF_NULL_TEX

    column = 0
    row = 0

    #those are the actual points of the blender surface to translate to idTechX patch "data" and "control" points
    # the first 4 are the "data" points and then the 5 next are the "control" points
    l_points = [0,1,2,4,5,6,8,9,10]

    file.write('// surf "%s"\n' % (obj.name))
    patch_num += 1
    if len(obj.material_slots) == 0:
        mat_name = PREF_NULL_TEX
    else:
        mat_name = obj.material_slots[0].name
    file.write('{\npatchDef2\n{\n"%s"\n' % (mat_name)) #FIXME chenge for the specific texture of the surface instead of the default one
    file.write('( 3 3 0 0 0 )\n') #TODO add the correct texture coordinates: ( xoffset yoffset rotation xscale yscale )
    file.write('(\n')

    for pt in l_points: #which are 9 point that should be writen in 3X3 matrix, the first four are data points and the next are control points
        #each point should be this way: ( x y z u v ) where u and v are the Bezier “blossom” coordinates
        if column == 0:
            file.write('( ')

        if( column <= 2 ):            
            #all the patches points are in "splines[0]"
            point = mathutils.Vector((0.0, 0.0, 0.0)) + obj.data.splines[0].points[pt].co.xyz
            #let's add the location and scaling of the object that unexpectedly doesn't multipliying the point by the matrix_world
            #point = point + obj.location
            #point = point.cross( obj.scale )
            
            i = 0
            while( i <= 2 ):
                point[i] = ( point[i] + obj.location[i] ) * obj.scale[i]
                i += 1
            
            #point = point * obj.matrix_world #it doesn't apply any
            point *= PREF_SCALE
            l_cleanresults = [clean_floats(point.x), clean_floats(point.y), clean_floats(point.z)]
            #TODO work out the Bezier “blossom” coordinates, this should not be dependant of the point but on actual UV mapping!
            #https://web.archive.org/web/20081011060118/http://quark.planetquake.gamespy.com/infobase/src.pas.bezier.html#quadmath
            texU = row * 0.5 #this is all false
            texV = column * 0.5
            column += 1
            file.write('( '+ l_cleanresults[0] + ' ' + l_cleanresults[1] + ' ' + l_cleanresults[2] + ' %s %s ) ' % (texU, texV))

        if column == 3:
            column = 0
            row += 1
            file.write(')\n')

    file.write(')\n')
    file.write('}\n}\n') #end of "patchDef2" function

#entity is a list with a key-val vars system.
def entity_export(scene, file):
    global entity_num
    global l_entities

    for e in l_entities:
        itsnum = entity_num
        file.write('// entity %i\n' % (itsnum))
        file.write('{\n')
        entity_num += 1
        for keyVal in e:
            if keyVal[0] == 'brush_data':
                brushDef3_export(scene, keyVal[1], file)
            elif keyVal[0] == 'patch_data':
                patchDef2_export(scene, keyVal[1], file)
            else:
                file.write('"%s" "%s"\n' % (keyVal[0], keyVal[1]))
        file.write('} //end of entity %i\n' % (itsnum)) #closing whatever entity we have there

def gather_idTechX_data(context):
    #TODO TODO TODO FIXME TODO TODO TODO
    global l_brushes
    global l_patches
    global l_meshes #TODO not yet used
    global l_entities

    print("create list for exporting elements")
    whatslegal = ['brushes', 'surf', 'entities', 'lights'] #FIXME not yet used
    l_legal_exports = []
    #TODO create the legal exports list, and ignore whatever is not a legal export
    
    for obj in context.selected_objects:
        if obj.type == 'MESH':
            l_brushes.append(obj)
        elif obj.type == 'SURFACE':
            l_patches.append(obj)

def export_map(context, filepath):    
    import time
    global entity_num
    global brush_num
    global mesh_num
    global patch_num
    global l_brushes
    global l_meshes
    global l_patches
    global l_entities

    entity_num = 0
    brush_num = 0
    mesh_num = 0
    patch_num = 0

    l_meshes = []
    l_brushes = []
    l_patches = []
    l_entities = []

    t = time.time()
    
    scene = context.scene

    print("opening file")
    file = open(filepath, 'w')

    gather_idTechX_data(context)

    if l_meshes or l_brushes or l_patches:
            #TODO brushes, patches and meshesmust be under worldspan entity
        print("since there are brushes or surfaces let's create a worldspawn entity")
        file.write('Version 2\n')
        create_worldspawn()
        hack_info_player_start() #It's a HACK!
        hack_light() #another one
        entity_export(scene, file) #the real deal happens here

    else:
        file.close() #FIXME ATM let's not close two times the file
        raise RuntimeError('found nothing to export!')

    print("closing file")
    file.close()

    print("Exported Map in %.4fsec" % (time.time() - t))

def save(operator,
         context,
         filepath=None,
         global_scale=100.0,
         face_thickness=0.1,
         texture_null="textures/bl/dev/16x16_gray",
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
