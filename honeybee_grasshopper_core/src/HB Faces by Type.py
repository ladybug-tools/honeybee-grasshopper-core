# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Separate the faces/sub-faces of honeybee Rooms, Faces, Apertures, Doors, or Shades
by object and face type.
-

    Args:
        _hb_objs: Honeybee Rooms, Faces, Apertures, Doors and/or Shades which will be
            separated based on object and face type. This can also be an entire
            honeybee Model.

    Returns:
        walls:The Walls with an Outdoors or Ground boundary condition.
        interior_walls: The Walls with a Surface or Adiabatic boundary condition.
        roofs: The RoofCeilings with an Outdoors or Ground boundary condition.
        ceilings: The RoofCeilings with a Surface or Adiabatic boundary condition.
        exterior_floors: The Floors with an Outdoors or Ground boundary condition.
        interior_floors: The Floors with a Surface or Adiabatic boundary condition.
        air_walls: The AirWalls.
        apertures: The Apertures with an Outdoors boundary condition.
        interior_apertures: The Apertures with a Surface boundary condition.
        doors: The Doors with an Outdoors boundary condition.
        interior_doors: The Doors with a Surface boundary condition.
        outdoor_shades: The Shades assigned to the outdoors of their parent objects.
            This also includes all orphaned shades of a model.
        indoor_shades: The Shades assigned to the indoors of their parent objects.
"""

ghenv.Component.Name = 'HB Faces by Type'
ghenv.Component.NickName = 'FacesByType'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '2 :: Organize'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

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
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee.boundarycondition import Adiabatic
except ImportError:  # honeybee-energy not installed
    Adiabatic = None  # don't worry about Aidabatic; Surface is the only interior bc


def add_shade(hb_obj):
    """Add an object's shades to the relevant lists."""
    outdoor_shades.extend([shd for shd in hb_obj.outdoor_shades])
    indoor_shades.extend([shd for shd in hb_obj.indoor_shades])

def add_door(dr):
    """Add a door to the relevant lists."""
    bc = dr.boundary_condition
    add_shade(dr)
    if isinstance(bc, Surface):
        interior_doors.append(dr)
    else:
        doors.append(dr)

def add_aperture(ap):
    """Add an aperture to the relevant lists."""
    bc = ap.boundary_condition
    add_shade(ap)
    if isinstance(bc, Surface):
        interior_apertures.append(ap)
    else:
        apertures.append(ap)

def add_face(face):
    """Add a face to the relevant lists."""
    add_shade(face)
    bc = face.boundary_condition
    type = face.type
    if isinstance(type, Wall):
        if isinstance(bc, (Surface, Adiabatic)):
            interior_walls.append(face)
        else:
            walls.append(face)
    elif isinstance(type, RoofCeiling):
        if isinstance(bc, (Surface, Adiabatic)):
            ceilings.append(face)
        else:
            roofs.append(face)
    elif isinstance(type, Floor):
        if isinstance(bc, (Surface, Adiabatic)):
            interior_floors.append(face)
        else:
            exterior_floors.append(face)
    elif isinstance(type, AirBoundary):
        air_walls.append(face)

    # add the apertures, doors, and shades
    for ap in face.apertures:
        add_aperture(ap)
    for dr in face.doors:
        add_door(dr)


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    walls = []
    interior_walls = []
    roofs = []
    ceilings = []
    exterior_floors = []
    interior_floors = []
    air_walls = []
    apertures = []
    interior_apertures = []
    doors = []
    interior_doors = []
    outdoor_shades = []
    indoor_shades = []

    # loop through all objects and add them
    for obj in _hb_objs:
        if isinstance(obj, Model):
            for room in obj.rooms:
                for face in room.faces:
                    add_face(face)
            for face in obj.orphaned_faces:
                add_face(face)
            for ap in obj.orphaned_apertures:
                add_aperture(ap)
            for dr in obj.orphaned_doors:
                add_door(dr)
            outdoor_shades.extend([shd for shd in obj.orphaned_shades])
        elif isinstance(obj, Room):
            add_shade(obj)
            for face in obj:
                add_face(face)
        elif isinstance(obj, Face):
            add_face(obj)
        elif isinstance(obj, Aperture):
            add_aperture(obj)
        elif isinstance(obj, Door):
            add_door(obj)
        elif isinstance(obj, Shade):
            outdoor_shades.append(obj)