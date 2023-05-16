# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Color Honeybee Faces, Apertures, Doors and Shades in the Rhino scene using
their attributes.
_
This can be used as a means to check that correct properties are assigned to
different faces.
-

    Args:
        _hb_objs: An array of honeybee Rooms, Faces, Apertures, Doors or Shades
            to be colored with their attributes in the Rhino scene. This can
            also be an entire Model to be colored.
        _attribute: Text for the name of the attribute with which the faces or
            sub-faces should be labeled. The Honeybee "Face Attributes" component
            lists all of the core attributes of the room. Also, each Honeybee
            extension (ie. Radiance, Energy) includes its own component that lists
            the face and sub-face attributes of that extension.
        legend_par_: An optional LegendParameter object to change the display
            of the colored faces and sub-faces (Default: None).

    Returns:
        mesh: Meshes of the faces and sub-faces colored according to their attributes.
        legend: Geometry representing the legend for colored meshes.
        wire_frame: A list of lines representing the outlines of the _hb_objs.
        values: A list of values noting the attribute assigned to each face/sub-face.
        colors: A list of colors noting the color of each face/sub-face in the
            Rhino scene. This can be used in conjunction with the native
            Grasshopper "Custom Preview" component to create custom
            visualizations in the Rhino scene.
        vis_set: An object containing VisualizationSet arguments for drawing a detailed
            version of the ColorRoom in the Rhino scene. This can be connected to
            the "LB Preview Visualization Set" component to display this version
            of the visualization in Rhino.
"""

ghenv.Component.Name = 'HB Color Face Attributes'
ghenv.Component.NickName = 'ColorFaceAttr'
ghenv.Component.Message = '1.6.2'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from ladybug.graphic import GraphicContainer
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.colorobj import ColorFace
    from honeybee.search import get_attr_nested
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3ds_to_colored_mesh, \
        from_face3d_to_wireframe
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.config import units_system
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# dictionary of unit-sensitive propperties to be handled specially
UNIT_SENSITIVE = {
    'properties.energy.r_factor': 'R Factor',
    'properties.energy.u_factor': 'U Factor',
    'properties.energy.shgc': 'SHGC'
}


if all_required_inputs(ghenv.Component):
    # extract any faces from input Rooms or Models
    faces = []
    for hb_obj in _hb_objs:
        if isinstance(hb_obj, Model):
            for room in hb_obj.rooms:
                faces.extend(room.faces)
                faces.extend(room.shades)
            faces.extend(hb_obj.orphaned_faces)
            faces.extend(hb_obj.orphaned_apertures)
            faces.extend(hb_obj.orphaned_doors)
            faces.extend(hb_obj.orphaned_shades)
        elif isinstance(hb_obj, Room):
            faces.extend(hb_obj.faces)
            faces.extend(hb_obj.shades)
        else:
            faces.append(hb_obj)

    # create the ColorFace visualization object
    color_obj = ColorFace(faces, _attribute, legend_par_)
    # if the U-factor is requested, compute it in a unit-sensitive way
    if _attribute in UNIT_SENSITIVE:
        nd = color_obj.legend_parameters.decimal_count
        units = units_system()
        values, flat_geo = [], []
        for face_obj in color_obj.flat_faces:
            try:
                obj_method = get_attr_nested(face_obj, _attribute, cast_to_str=False)
                values.append(round(obj_method(units), nd))
                if isinstance(face_obj, Face):
                    flat_geo.append(face_obj.punched_geometry)
                else:
                    flat_geo.append(face_obj.geometry)
            except TypeError:
                pass  # shade geometry
        l_par = color_obj.legend_parameters.duplicate()
        l_par.title = UNIT_SENSITIVE[_attribute]
        graphic = GraphicContainer(values, color_obj.min_point, color_obj.max_point, l_par)
        color_obj._attributes = tuple(str(v) for v in values)
        attributes_unique = [v for v in set(values)]
        attributes_unique.sort()
        color_obj._attributes_unique = tuple(str(val) for val in attributes_unique)
        color_obj._flat_geometry = flat_geo
    else:
        graphic = color_obj.graphic_container
        values = color_obj.attributes_original
        flat_geo = color_obj.flat_geometry

    # output the visualization geometry
    mesh = [from_face3ds_to_colored_mesh([fc], col) for fc, col in
            zip(flat_geo, graphic.value_colors)]
    wire_frame = []
    for face in color_obj.flat_faces:
        wire_frame.extend(from_face3d_to_wireframe(face.geometry))
    legend = legend_objects(graphic.legend)
    colors = [color_to_color(col) for col in graphic.value_colors]
    vis_set = color_obj
