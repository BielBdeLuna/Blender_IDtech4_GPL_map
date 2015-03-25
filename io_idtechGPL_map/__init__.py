## this file is GPL v3
## based partly on Campbell Barton's MAP script
## Biel Bestué de Luna

bl_info = {
    "name": "idtech GPL MAP level",
    "author": "Biel Bestué de Luna",
    "version": (0, 0, 0),
    "blender": (2, 57, 0),
    "location": "File > Import-Export",
    "description": "Import-Export MAP levels",
    "warning": "",
    "wiki_url": "",
    "support": 'NONE',
    "category": "Import-Export"
}

if "bpy" in locals():
    import imp
    if "import_map" in locals():
        imp.reload(import_obj)
    if "export_map" in locals():
        imp.reload(export_obj)

import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper




