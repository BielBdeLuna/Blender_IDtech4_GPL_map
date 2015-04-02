## this file is GPL v3
## based partly on Campbell Barton's "export quake map" script
## Biel Bestué de Luna

bl_info = {
    "name": "Export idTechX map",
    "author": "Biel Bestué de Luna",
    "version": (0, 0, 0),
    "blender": (2, 70, 0),
    "location": "File > Import-Export",
    "description": "Import-Export idTechX map levels",
    "warning": "",
    "wiki_url": "",
    "support": 'TESTING',
    "category": "Import-Export"
}

if "bpy" in locals():
    import imp
    if "export_map" in locals():
        imp.reload(export_map)
    if "import_map" in locals():
        imp.reload(import_map)
    
import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty #those are the fields of the UI
from bpy_extras.io_utils import ExportHelper #this is the type of element open when selecting the option to export, that is the window ehere you cans et up the name and such
from bpy_extras.io_utils import ImportHelper # for the future

class export_map_helper(bpy.types.Operator, ExportHelper): #this class then inherits the ExportHelper capabilities
    """Export whole level or selected objects to a idTechX map"""

    bl_idname = "export_scene.idtechx_map" #does this exist?
    bl_label = "Export Map"
    bl_options = {'PRESET'}

    filename_ext = ".map"
    filter_glob = StringProperty(default="*.map", options={'HIDDEN'})

    global_scale = FloatProperty(
            name="Scale",
            description="Scale everything by this value",
            min=0.01, max=1000.0,
            default=100.0,
    )
    grid_snap = BoolProperty(
            name="Grid Snap",
            description="Round to whole numbers",
            default=False,
    )
    texture_null = StringProperty(
            name="Tex Null",
            description="Texture used when none is assigned",
            default="NULL",
    )

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        keywords = self.as_keywords(ignore=("check_existing", "filter_glob"))

        from . import export_map
        return export_map.save(self, context, **keywords)
    

def ui_func(self, context):
    self.layout.operator(export_map_helper.bl_idname, text="idTechX MAP (.map)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_export.append(ui_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_export.remove(ui_func)

if __name__ == "__main__":
    register()
