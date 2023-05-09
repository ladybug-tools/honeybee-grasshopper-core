# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Lablel Honeybee rooms with their attributes in the Rhino scene.
_
This can be used as a means to check that correct properties are assigned to
different Rooms.
-

    Args:
        _rooms_model: An array of honeybee Rooms or honeybee Models to be labeled
            with their attributes in the Rhinoscene.
        _attribute_: Text for the name of the Room attribute with which the
            Rooms should be labeled. The Honeybee "Room Attributes" component
            lists all of the core attributes of the room. Also, each Honeybee
            extension (ie. Radiance, Energy) includes its own component that
            lists the Room attributes of that extension. Default: "name".
        _txt_height_: An optional number for the height of the text in the Rhino
            scene.  The default is auto-calculated based on the dimensions of the
            input geometry.
        _font_: An optional name of a font in which the labels will display. This
            must be a font that is installed on this machine in order to work
            correctly. Default: "Arial".

    Returns:
        label_text: The text with which each of the rooms are labeled.
        base_pts: The base planes for each of the text labels.
        labels: The text objects that are displaying within the Rhino scene.
        wire_frame: A list of curves representing the outlines of the rooms.
            This is useful for understanding which geometry elements each
            label corresponds to.
"""

ghenv.Component.Name = "HB Label Rooms"
ghenv.Component.NickName = 'LabelRooms'
ghenv.Component.Message = '1.6.2'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d import Vector3D, Point3D, Polyline3D, \
        Plane, Face3D, Polyface3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.facetype import Floor
    from honeybee.search import get_attr_nested
    from honeybee.units import parse_distance_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_polyface3d_to_wireframe, from_plane
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.config import conversion_to_meters, units_system, tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# hide the base_pts output from the scene
ghenv.Component.Params.Output[1].Hidden = True
# maximum text height in meters - converted to model units
max_txt_h = 0.25 / conversion_to_meters()
max_txt_v = 1.0 / conversion_to_meters()
# tolerance for computing the pole of inaccessibility
p_tol = parse_distance_string('0.01m', units_system())


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    label_text = []
    base_pts = []
    labels = []
    wire_frame = []

    # set the default attribute and font
    if _attribute_ is None:
        _attribute_ = 'display_name'
    if _font_ is None:
        _font_ = 'Arial'

    # extract any rooms from input Models
    rooms = []
    for hb_obj in _rooms_model:
        if isinstance(hb_obj, Model):
            rooms.extend(hb_obj.rooms)
        else:
            rooms.append(hb_obj)

    for room in rooms:
        # get the attribute to be displayed
        room_prop = get_attr_nested(room, _attribute_)
        # compute the center point for the text
        room_h = room.geometry.max.z - room.geometry.min.z
        m_vec = Vector3D(0, 0, max_txt_v) if room_h > max_txt_v * 2 \
            else Vector3D(0, 0, room_h / 2)
        floor_faces = [face.geometry for face in room.faces if isinstance(face.type, Floor)]
        if len(floor_faces) == 1:
            flr_geo = floor_faces[0]
            base_pt = flr_geo.center if flr_geo.is_convex else \
                flr_geo.pole_of_inaccessibility(p_tol)
        elif len(floor_faces) == 0:
            c_pt = room.geometry.center
            base_pt = Point3D(c_pt.x, c_pt.y, room.geometry.min.z)
        else:
            floor_p_face = Polyface3D.from_faces(floor_faces, tolerance)
            floor_outline = Polyline3D.join_segments(floor_p_face.naked_edges, tolerance)[0]
            flr_geo = Face3D(floor_outline.vertices[:-1])
            base_pt = flr_geo.center if flr_geo.is_convex else \
                flr_geo.pole_of_inaccessibility(p_tol)
        base_pt = base_pt.move(m_vec)
        base_plane = Plane(Vector3D(0, 0, 1), base_pt)
        # determine the text height
        if _txt_height_ is None:  # auto-calculate default text height
            txt_len = len(room_prop) if len(room_prop) > 10 else 10
            txt_h = (room.geometry.max.x - room.geometry.min.x) / txt_len
        else:
            txt_h = _txt_height_
        txt_h = max_txt_h if txt_h > max_txt_h else txt_h
        # create the text label
        label = text_objects(room_prop, base_plane, txt_h, font=_font_,
                             horizontal_alignment=1, vertical_alignment=3)

        # append everything to the lists
        label_text.append(room_prop)
        base_pts.append(from_plane(base_plane))
        labels.append(label)
        wire_frame.extend(from_polyface3d_to_wireframe(room.geometry))