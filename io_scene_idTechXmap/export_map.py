## this file is GPL v3
## based partly on Campbell Barton's "export quake map" script
## Biel Bestué de Luna

import bpy
import math
import mathutils
#import bl_processing

#processing
#present the input floats as like either integers or floats depending on their true nature and also with a correct sign, but present them as a strings to the code
def clean_floats( flo ):
    if flo.is_integer():
        flo = "%.0f" % ( flo )
        if True:
             #for those odd "-0" cases
            if flo == -0:
                flo = 0                
    else:
        #flo = "%.8f" % ( flo )
        #from http://stackoverflow.com/questions/2440692/formatting-floats-in-python-without-superfluous-zeros
        flo = ( '%f' % flo ).rstrip( '0' ).rstrip( '.' )

    return "%s" % (flo)

#idTechX related
def apply_transforms( offset, scale, rotation, spot, homothetic_scale ):
    #first apply offset transform and scale transform  
    result = mathutils.Vector()
    i = 0
    while( i <= 2 ):
        result[i] = ( spot[i] + offset[i] ) * scale[i]
        i += 1
   
    # now apply rotation transforms
    #TODO
    
    #apply the homothetic scale too ( scale equal in all dimensions )
    result *= homothetic_scale

    return result

def DEG2RAD(degrees):
    return degrees * math.pi / 180

def get_the_three_common_degrees_of_freedom( obj ):
    result = []

    location = mathutils.Vector( obj.location + obj.delta_location )
    result.append( location )
    scale = mathutils.Vector( obj.scale + obj.delta_scale )
    result.append( scale )
    rotation_x = obj.rotation_euler.x + obj.delta_rotation_euler.x #so quirky
    rotation_y = obj.rotation_euler.y + obj.delta_rotation_euler.y
    rotation_z = obj.rotation_euler.z + obj.delta_rotation_euler.z
    rotation = mathutils.Vector( ( rotation_x, rotation_y, rotation_z ) )
    result.append( rotation )

    return result


class entity(object):
    def __init__( self ):
        self.name = ''
        self.keyValPairs = []
        self.brushesOwned = []
        self.patchesOwned = []

    def add_key_val( self, key, value ):
        keyVal = []
        keyVal.append( key )
        keyVal.append( value )
        if value == 'worldspawn':
            self.name = value
        else:
            if key == 'name':
                self.name = value
        self.keyValPairs.append( keyVal )
    
    def add_brush( self, brush ):
        self.brushesOwned.append( brush )

    def add_patch( self, patch ):
        self.patchesOwned.append( patch )

    def export( self, num ):        
        export_text = '// entity %i\n{\n' % ( num )
        if len( self.keyValPairs ) > 0:
            for kv in self.keyValPairs:
                export_text += '"%s" "%s"\n' % ( kv[0], kv[1] )    
        if len( self.brushesOwned ) > 0:
            for b in self.brushesOwned:
                export_text += b.export_brush()
        if False:
            if len( self.patchesOwned ) > 0:
                for p in self.patchesOwned:
                    export_text += p.export_patch()

        export_text += '} //end of entity %i\n' % ( num )
        return export_text

class patch( object ):
    def __init__( self, obj ):
        self.Bobj = obj
        self.name = self.Bobj.name
        self.entity_owner = ''
        self.l_points = [0,1,2,4,5,6,8,9,10] #those are fixed points in blender

        offscalrot = get_the_three_common_degrees_of_freedom( self.Bobj )
        self.offset = mathutils.Vector( offscalrot[0] )
        self.scale = mathutils.Vector( offscalrot[1] )
        self.rotation = mathutils.Vector( offscalrot[2] )

        if len( self.Bobj.material_slots ) == 0:
            self.material = PREF_NULL_TEX
        else:
            self.material = self.Bobj.material_slots[0].name

        #work out a way to gather the texturing
        self.UV_offset = [ 0.0, 0.0 ]
        self.UV_scale = [ 1.0, 1.0 ]
        self.UV_rotation = 0.0

    def set_owner( self, owner ):
        self.entity_owner = owner        

    def export_patch( self ):
        global patch_num
        global PREF_SCALE     

        column = 0
        row = 0

        #export_text = '// surf %i : "%s"\n{\npatchDef2\n{\n"%s"\n' % ( patch_num, self.name, self.material )
        export_text = '// surf %i\n{\npatchDef2\n{\n"%s"\n' % ( patch_num, self.material )
        patch_num += 1

        clean_text = []
        clean_text.append( clean_floats( self.UV_offset[0] ) )
        clean_text.append( clean_floats( self.UV_offset[1] ) )
        clean_text.append( clean_floats( self.UV_rotation ) )
        clean_text.append( clean_floats( self.UV_scale[0] ) )
        clean_text.append( clean_floats( self.UV_scale[1] ) )         
        export_text += '( %s %s %s %s %s )\n(\n' % ( clean_text[0], clean_text[1], clean_text[2], clean_text[3], clean_text[4] )

        for pt in self.l_points:
            if column == 0:
                export_text += '( '

            if( column <= 2 ):            
            
                point = mathutils.Vector((0.0, 0.0, 0.0)) + self.Bobj.data.splines[0].points[pt].co.xyz
            
                point = apply_transforms( self.offset, self.scale, self.rotation, point, PREF_SCALE )

                l_clean_point = [] #need to create a function for this!
                l_clean_point.append( clean_floats( point.x ) )
                l_clean_point.append( clean_floats( point.y ) )
                l_clean_point.append( clean_floats( point.z ) )
                
                
                if True: #FIXME this only should apply when there are no UV set by the user, as this is generic
                    texU = row * 0.5 #this is a hack
                    texV = column * 0.5
                column += 1
                export_text += '( %s %s %s %s %s ) ' % ( l_clean_point[0], l_clean_point[1], l_clean_point[2], clean_floats( texU ), clean_floats( texV ) )

            if column == 3:
                column = 0
                row += 1
                export_text += ')\n'

        export_text += ')\n}\n}\n' #end of "patchDef2" function
        return export_text

class brush(object):
    class plane(object):
        def __init__( self, normal, distance, material, UV_offset, UV_rotation, UV_scale ):
            self.normal = []
            self.normal.append( clean_floats( normal.x ) )
            self.normal.append( clean_floats( normal.y ) )
            self.normal.append( clean_floats( normal.z ) )
            self.distance = clean_floats( distance )
            self.material = material
            self.m_texture = [] #the texture matrix           
            self.m_texture.append( clean_floats( UV_scale[0] * math.cos( DEG2RAD( UV_rotation ) ) ) )
            self.m_texture.append( clean_floats( -1.0 * UV_scale[1] * math.sin( DEG2RAD( UV_rotation ) ) ) )
            self.m_texture.append( clean_floats( -1.0 * UV_offset[0] ) )
            self.m_texture.append( clean_floats( UV_scale[0] * math.sin( DEG2RAD( UV_rotation ) ) ) )
            self.m_texture.append( clean_floats( UV_scale[1] * math.cos( DEG2RAD( UV_rotation ) ) ) )
            self.m_texture.append( clean_floats( UV_offset[1] ) )

    def __init__( self, obj ):
        global PREF_SCALE

        self.Bobj = obj
        self.name = self.Bobj.name
        self.entity_owner = ''
        self.l_planes = []

        offscalrot = get_the_three_common_degrees_of_freedom( self.Bobj )
        self.offset = mathutils.Vector( offscalrot[0] )
        self.scale = mathutils.Vector( offscalrot[1] )
        self.rotation = mathutils.Vector( offscalrot[2] )

        #work out a way to gather the texturing
        self.UV_offset = [ 0.0, 0.0 ]
        self.UV_scale = [ 1.0 * ( 1.0 / PREF_SCALE ), 1.0 * ( 1.0 / PREF_SCALE ) ] #FIXME this shouldn't need the PREF_SCALE, at least not at exporting!
        self.UV_rotation = 0.0

        self.check_brush_integrity()

    def check_brush_integrity( self ):
        #TODO check if all the vertex on it's concave poligons are coplanar ( they are in the same plane )
        #TODO and check in there is any other strangenes with it's polygons ( any convex polygons, or any polygon that shares the plane with another polygon )
        #TODO repair if it need to be rapired
        pass   

    def set_owner( self, owner ):
        self.entity_owner = owner       

    def gather_planes( self ):
        global PREF_SCALE
        global PREF_NULL_TEX

        #mesh = self.Bobj.to_mesh(scene, True, 'PREVIEW')
        for poly in self.Bobj.data.polygons:
            #from every face of a brush we need:
            #the normal of the surface
            #a vertex on the surface (that we know it's position) will help us define the surface
            #put that vertex in the world context, where it is?
            #calculate the minimum distance between the surface and the world origin (eucleidan distance?)
            #scale that distance by the scale on the exporter
            normal = poly.normal

            vert = mathutils.Vector((0.0, 0.0, 0.0)) + self.Bobj.data.vertices[poly.vertices[0]].co
            vert = apply_transforms( self.offset, self.scale, self.rotation, vert, 1.0 ) #PREF_SCALE is not needed here so just 1.0 ( no isotropic scaling )

            dist = mathutils.geometry.distance_point_to_plane( mathutils.Vector((0.0,0.0,0.0)), vert, normal ) * PREF_SCALE

            #gather the material per plane ( TODO find out a way to give every polygon of the mesha different material )
            if len(self.Bobj.material_slots) == 0:
                mat_name = PREF_NULL_TEX
            else:
                mat_name = self.Bobj.material_slots[0].name
            
            new_plane = self.plane( normal, dist, mat_name, self.UV_offset, self.UV_rotation, self.UV_scale )
            self.l_planes.append( new_plane )

    def export_planes( self ):
        text_planes = ""
        for plane in self.l_planes:
            text = '( %s %s %s %s ) ' % ( plane.normal[0], plane.normal[1], plane.normal[2], plane.distance )
            text += '( ( %s %s %s ) ' % ( plane.m_texture[0], plane.m_texture[1], plane.m_texture[2] )
            text += '( %s %s %s ) ) ' % ( plane.m_texture[3], plane.m_texture[4], plane.m_texture[5] )
            text +='"%s" ' % ( plane.material )
            text +='0 0 0\n' #the use of those final numbers is yet unknown
            text_planes += text
        return text_planes

    def export_brush( self ):
        global brush_num

        self.gather_planes()

        export_text = '// brush %i : "%s"\n{\nbrushDef3\n{\n' % (brush_num, self.name)
        brush_num += 1
        export_text += self.export_planes()
        export_text += '}\n}\n'
        return export_text
        
        
        
global entity_num
def hack_info_player_start():
    global l_entities

    ent_info_player_start = entity()
    ent_info_player_start.add_key_val( 'classname', 'info_player_start' )
    ent_info_player_start.add_key_val( 'name', 'info_player_start_1' )
    ent_info_player_start.add_key_val( 'angle', '270' )
    ent_info_player_start.add_key_val( 'origin', '0 0 32' )
    l_entities.append(ent_info_player_start)

def hack_light():
    global l_entities
    
    ent_spot_light = entity()
    ent_spot_light.add_key_val( 'classname', 'light' )
    ent_spot_light.add_key_val( 'name', 'light_1' )
    ent_spot_light.add_key_val( 'light_center', '0 0 0' )
    ent_spot_light.add_key_val( 'light_radius', '600 600 600' )
    ent_spot_light.add_key_val( 'origin', '0 0 96' )
    l_entities.append(ent_spot_light)

def create_worldspawn():
    global l_entities

    ent_worldspawn = entity()
    ent_worldspawn.add_key_val( 'classname', 'worldspawn' )

    l_entities.append( ent_worldspawn )

def IDTECHX_API_even_more_related_stuff():
    global l_entities
    global l_brushes
    global l_patches
    
    #FIXME not all pathes or brushes will be owned by the Worldspawn, so it needs and infraestructure to determine what is form who.
    for obj in l_brushes:
        new_brush = brush( obj ) # this shouldn't be here
        new_brush.set_owner( l_entities[0].name ) # nor this
        l_entities[0].add_brush( new_brush )
    for obj in l_patches:
        new_patch = patch( obj ) 
        new_patch.set_owner( l_entities[0].name )
        l_entities[0].add_patch( new_patch )
"""
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
"""
#entity is a list with a key-val vars system.
def entity_export(scene, file):
    global entity_num
    global l_entities

    for e in l_entities:
        file.write( e.export( entity_num ) )
        entity_num += 1

def IDTECHX_API_more_related_stuff(context):
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

def IDTECHX_API_related_stuff():
    global l_entities
    global entity_num

    entity_num = 0

    l_entities = []

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

    brush_num = 0
    mesh_num = 0
    patch_num = 0

    l_meshes = []
    l_brushes = []
    l_patches = []

    scene = context.scene  

    IDTECHX_API_related_stuff()

    IDTECHX_API_more_related_stuff(context)

    if l_meshes or l_brushes or l_patches:
            #TODO brushes, patches and meshesmust be under worldspan entity
        print("since there are brushes or surfaces let's create a worldspawn entity")
        create_worldspawn()
        IDTECHX_API_even_more_related_stuff()
        hack_info_player_start() #It's a HACK!
        hack_light() #another one
        
        t = time.time()
        print("opening file")
        file = open(filepath, 'w')
        file.write('Version 2\n')
        entity_export(scene, file) #the real deal happens here
        print("closing file")
        file.close()
        print("Exported Map in %.4fsec" % (time.time() - t))

    else:
        raise RuntimeError('found nothing to export!')
    

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
