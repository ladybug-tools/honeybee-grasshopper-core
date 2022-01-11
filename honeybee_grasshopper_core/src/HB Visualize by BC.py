# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Visualize room geometry in the Rhino scene organized by boundary condition.
-

    Args:
        _hb_objs: A Honeybee Model, Room, Face, Aperture, Door or Shade to be
            previewed in the Rhino scene based on boundary condition.

    Returns:
        outdoors: Rhino geometry for the objects with an Outdoors boundary condition.
        surface: Rhino geometry for the objects with a Surface (interior) boundary
            condition.
        ground: Rhino geometry for the objects with a Ground boundary condition.
        adiabatic: Rhino geometry for the objects with an adiabatic (no heat flow)
            boundary condition.
        other: Rhino geometry for all objects with a boundary condition other than
            the four above. All shade geometry will also be added to this list.
        wire_frame: A list of lines representing the outlines of the rooms.
"""

ghenv.Component.Name = "HB Visualize by BC"
ghenv.Component.NickName = 'VizByBC'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

try:  # import the ladybug dependencies
    from ladybug.color import Colorset
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
    from honeybee.door import Door
    from honeybee.shade import Shade
    from honeybee.boundarycondition import Outdoors, Surface, Ground
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3ds_to_colored_mesh, \
        from_face3d_to_wireframe
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee.boundarycondition import Adiabatic
except ImportError:  # honeybee-energy is not installed
    Adiabatic = None  # don't worry about the Adiabatic bc


def add_shades(hb_obj):
    """Add assigned shade objects to the relevant list."""
    _other.extend([shd.geometry for shd in hb_obj.shades])


def add_subface(ap, geo_list=None):
    """Add an aperture or a door to the relevant lists."""
    add_shades(ap)
    if geo_list is None:
        geo_list = _outdoors if isinstance(ap.boundary_condition, Outdoors) \
            else _surface
    geo_list.append(ap.geometry)


def add_face(face):
    """Add a Face to the relevant lists."""
    add_shades(face)
    bc = face.boundary_condition
    if isinstance(bc, Outdoors):
        geo_list = _outdoors
    elif isinstance(bc, Surface):
        geo_list = _surface
    elif isinstance(bc, Ground):
        geo_list = _ground
    elif isinstance(bc, Adiabatic):
        geo_list = _adiabatic
    else:
        geo_list = _other
    geo_list.append(face.punched_geometry)
    for ap in face.apertures:
        add_subface(ap, geo_list)
    for dr in face.doors:
        add_subface(dr, geo_list)


def add_room(room):
    """Add a Room to the relevant lists."""
    add_shades(room)
    for face in room:
        add_face(face)


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    _outdoors = []
    _surface = []
    _ground = []
    _adiabatic = []
    _other = []

    # loop through the objects and group them by boundary condition
    for hb_obj in _hb_objs:
        if isinstance(hb_obj, Model):
            [add_room(room) for room in hb_obj.rooms]
            [add_face(face) for face in hb_obj.orphaned_faces]
            [add_subface(ap) for ap in hb_obj.orphaned_apertures]
            [add_subface(dr) for dr in hb_obj.orphaned_doors]
            _other.extend([shd.geometry for shd in hb_obj.orphaned_shades])
        elif isinstance(hb_obj, Room):
            add_room(hb_obj)
        elif isinstance(hb_obj, Face):
            add_face(hb_obj)
        elif isinstance(hb_obj, Aperture):
            add_subface(hb_obj)
        elif isinstance(hb_obj, Door):
            add_subface(hb_obj)
        elif isinstance(hb_obj, Shade):
            _other.append(hb_obj.geometry)

    # color all of the geometry with its respective surface type
    palette = Colorset.openstudio_palette()
    outdoors = from_face3ds_to_colored_mesh(_outdoors, palette[9]) \
        if len(_outdoors) != 0 else None
    surface = from_face3ds_to_colored_mesh(_surface, palette[13]) \
        if len(_surface) != 0 else None
    ground = from_face3ds_to_colored_mesh(_ground, palette[2]) \
        if len(_ground) != 0 else None
    adiabatic = from_face3ds_to_colored_mesh(_adiabatic, palette[4]) \
        if len(_adiabatic) != 0 else None
    other = from_face3ds_to_colored_mesh(_other, palette[12]) \
        if len(_other) != 0 else None

    # create the wire frame
    all_geo = _outdoors + _surface + _ground + _adiabatic + _other
    wire_frame = [curve for face in all_geo for curve in from_face3d_to_wireframe(face)]
