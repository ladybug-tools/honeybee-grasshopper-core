# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Visualize room geometry in the Rhino scene organized by object and face type.
-

    Args:
        _hb_objs: A Honeybee Model, Room, Face, Aperture, Door or Shade to be
            previewed in the Rhino scene based on type.

    Returns:
        walls: Rhino geometry for the Walls with an Outdoors or Ground boundary
            condition.
        interior_walls: Rhino geometry for the Walls with a Surface or Adiabatic
            boundary condition.
        roofs: Rhino geometry for the RoofCeilings with an Outdoors or Ground
            boundary condition.
        ceilings: Rhino geometry for the RoofCeilings with a Surface or Adiabatic
            boundary condition.
        exterior_floors: Rhino geometry for the Floors with an Outdoors or Ground
            boundary condition.
        interior_floors: Rhino geometry for the Floors with a Surface or Adiabatic
            boundary condition.
        air_walls: Rhino geometry for the AirWalls.
        apertures: Rhino geometry for the Apertures with an Outdoors boundary condition.
        interior_apertures: Rhino geometry for the Apertures with a Surface
            boundary condition.
        doors: Rhino geometry for the Doors with an Outdoors boundary condition.
        interior_doors: Rhino geometry for the Doors with a Surface boundary condition.
        outdoor_shades: Rhino geometry for the Shades assigned to the outdoors of
            their parent objects. This also includes all orphaned shades
            of a model.
        indoor_shades: Rhino geometry for the Shades assigned to the indoors
            of their parent objects.
        wire_frame: A list of lines representing the outlines of the rooms.
"""

ghenv.Component.Name = 'HB Visualize by Type'
ghenv.Component.NickName = 'VizByType'
ghenv.Component.Message = '1.5.0'
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
    from honeybee.boundarycondition import Surface
    from honeybee.facetype import Wall, RoofCeiling, Floor, AirBoundary
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3ds_to_colored_mesh, \
        from_face3d_to_wireframe
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee.boundarycondition import Adiabatic
except ImportError:  # honeybee-energy not installed
    Adiabatic = None  # don't worry about Aidabatic; Surface is the only interior bc


def add_shade(hb_obj):
    """Add assigned shade objects to the relevant lists."""
    _outdoor_shades.extend([shd.geometry for shd in hb_obj.outdoor_shades])
    _indoor_shades.extend([shd.geometry for shd in hb_obj.indoor_shades])


def add_aperture(ap):
    """Add an aperture to the relevant lists."""
    add_shade(ap)
    if isinstance(ap.boundary_condition, Surface):
        _interior_apertures.append(ap.geometry)
    else:
        _apertures.append(ap.geometry)


def add_door(dr):
    """Add a door to the relevant lists."""
    add_shade(dr)
    if isinstance(dr.boundary_condition, Surface):
        _interior_doors.append(dr.geometry)
    else:
        _doors.append(dr.geometry)


def add_face(face):
    """Add a Face to the relevant lists."""
    add_shade(face)
    bc = face.boundary_condition
    type = face.type
    if isinstance(type, Wall):
        if isinstance(bc, (Surface, Adiabatic)):
            _interior_walls.append(face.punched_geometry)
        else:
            _walls.append(face.punched_geometry)
    elif isinstance(type, RoofCeiling):
        if isinstance(bc, (Surface, Adiabatic)):
            _ceilings.append(face.punched_geometry)
        else:
            _roofs.append(face.punched_geometry)
    elif isinstance(type, Floor):
        if isinstance(bc, (Surface, Adiabatic)):
            _interior_floors.append(face.punched_geometry)
        else:
            _exterior_floors.append(face.punched_geometry)
    elif isinstance(type, AirBoundary):
        _air_walls.append(face.punched_geometry)

    # add the apertures, doors, and shades
    for ap in face.apertures:
        add_aperture(ap)
    for dr in face.doors:
        add_door(dr)


def add_room(room):
    """Add a Room to the relevant lists."""
    add_shade(room)
    for face in room:
        add_face(face)


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    _walls = []
    _interior_walls = []
    _roofs = []
    _ceilings = []
    _exterior_floors = []
    _interior_floors = []
    _air_walls = []
    _apertures = []
    _interior_apertures = []
    _doors = []
    _interior_doors = []
    _outdoor_shades = []
    _indoor_shades = []

    # loop through the objects and group them by type
    for hb_obj in _hb_objs:
        if isinstance(hb_obj, Model):
            [add_room(room) for room in hb_obj.rooms]
            [add_face(face) for face in hb_obj.orphaned_faces]
            [add_aperture(ap) for ap in hb_obj.orphaned_apertures]
            [add_door(dr) for dr in hb_obj.orphaned_doors]
            _outdoor_shades.extend([shd.geometry for shd in hb_obj.orphaned_shades])
        elif isinstance(hb_obj, Room):
            add_room(hb_obj)
        elif isinstance(hb_obj, Face):
            add_face(hb_obj)
        elif isinstance(hb_obj, Aperture):
            add_aperture(hb_obj)
        elif isinstance(hb_obj, Door):
            add_door(hb_obj)
        elif isinstance(hb_obj, Shade):
            if hb_obj.is_indoor:
                _indoor_shades.append(hb_obj.geometry)
            else:
                _outdoor_shades.append(hb_obj.geometry)

    # color all of the geometry with its respective surface type
    palette = Colorset.openstudio_palette()
    walls = from_face3ds_to_colored_mesh(_walls, palette[0]) \
        if len(_walls) != 0 else None
    interior_walls = from_face3ds_to_colored_mesh(_interior_walls, palette[1]) \
        if len(_interior_walls) != 0 else None
    roofs = from_face3ds_to_colored_mesh(_roofs, palette[3]) \
        if len(_roofs) != 0 else None
    ceilings = from_face3ds_to_colored_mesh(_ceilings, palette[4]) \
        if len(_ceilings) != 0 else None
    exterior_floors = from_face3ds_to_colored_mesh(_exterior_floors, palette[6]) \
        if len(_exterior_floors) != 0 else None
    interior_floors = from_face3ds_to_colored_mesh(_interior_floors, palette[7]) \
        if len(_interior_floors) != 0 else None
    air_walls = from_face3ds_to_colored_mesh(_air_walls, palette[12]) \
        if len(_air_walls) != 0 else None
    apertures = from_face3ds_to_colored_mesh(_apertures, palette[9]) \
        if len(_apertures) != 0 else None
    interior_apertures = from_face3ds_to_colored_mesh(_interior_apertures, palette[9]) \
        if len(_interior_apertures) != 0 else None
    doors = from_face3ds_to_colored_mesh(_doors, palette[10]) \
        if len(_doors) != 0 else None
    interior_doors = from_face3ds_to_colored_mesh(_interior_doors, palette[10]) \
        if len(_interior_doors) != 0 else None
    outdoor_shades = from_face3ds_to_colored_mesh(_outdoor_shades, palette[11]) \
        if len(_outdoor_shades) != 0 else None
    indoor_shades = from_face3ds_to_colored_mesh(_indoor_shades, palette[11]) \
        if len(_indoor_shades) != 0 else None

    # create the wire frame
    all_geo = _walls + _interior_walls + _roofs + _ceilings + _exterior_floors + \
        _interior_floors + _air_walls + _apertures + _interior_apertures + _doors + \
        _interior_doors + _outdoor_shades + _indoor_shades
    wire_frame = [curve for face in all_geo for curve in from_face3d_to_wireframe(face)]