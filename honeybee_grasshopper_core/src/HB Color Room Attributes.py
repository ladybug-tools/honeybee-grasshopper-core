# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Color Honeybee rooms in the Rhino scene using their attributes.
_
This can be used as a means to check that correct properties are assigned to
different Rooms.
-

    Args:
        _rooms_model: An array of honeybee Rooms or honeybee Models to be colored
            with their attributes in the Rhino scene.
        _attribute: Text for the name of the Room attribute with which the
            Rooms should be labeled. The Honeybee "Room Attributes" component
            lists all of the core attributes of the room. Also, each Honeybee
            extension (ie. Radiance, Energy) includes its own component that
            lists the Room attributes of that extension.
        legend_par_: An optional LegendParameter object to change the display
            of the colored rooms (Default: None).

    Returns:
        mesh: Meshes of the room floors colored according to their attributes.
        legend: Geometry representing the legend for colored meshes.
        wire_frame: A list of lines representing the outlines of the rooms.
        values: A list of values that align with the input _rooms noting the
            attribute assigned to each room.
        colors: A list of colors that align with the input Rooms, noting the color
            of each Room in the Rhino scene. This can be used in conjunction
            with the native Grasshopper "Custom Preview" component and other
            honeybee visualization components (like "HB Visulaize Quick") to
            create custom visualizations in the Rhino scene.
        vis_set: An object containing VisualizationSet arguments for drawing a detailed
            version of the ColorRoom in the Rhino scene. This can be connected to
            the "LB Preview Visualization Set" component to display this version
            of the visualization in Rhino.
"""

ghenv.Component.Name = 'HB Color Room Attributes'
ghenv.Component.NickName = 'ColorRoomAttr'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.colorobj import ColorRoom
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3ds_to_colored_mesh, \
        from_polyface3d_to_wireframe
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models
    rooms = []
    for hb_obj in _rooms_model:
        if isinstance(hb_obj, Model):
            rooms.extend(hb_obj.rooms)
        else:
            rooms.append(hb_obj)

    # create the ColorRoom visualization object and output geometry
    color_obj = ColorRoom(rooms, _attribute, legend_par_)
    graphic = color_obj.graphic_container
    mesh = [from_face3ds_to_colored_mesh(flrs, col) for flrs, col in
            zip(color_obj.floor_faces, graphic.value_colors)]
    wire_frame = []
    for room in rooms:
        wire_frame.extend(from_polyface3d_to_wireframe(room.geometry))
    legend = legend_objects(graphic.legend)
    values = color_obj.attributes_original
    colors = [color_to_color(col) for col in graphic.value_colors]
    vis_set = color_obj