# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Separate the faces/sub-faces of honeybee Rooms, Faces, Apertures or Doors by
boundary condition.
-

    Args:
        _hb_objs: Honeybee Rooms, Faces, Apertures, Doors and/or Shades which will
            be separated based on boundary condition. This can also be an entire
            honeybee Model.
    
    Returns:
        outdoors: The faces with an Outdoors boundary condition.
        surface: The faces with a Surface (interior) boundary condition.
        ground: The faces with a Ground boundary condition.
        adiabatic: The faces with an adiabatic (no heat flow) boundary condition.
        other: All faces with a boundary condition other than the four above.
"""

ghenv.Component.Name = 'HB Faces by BC'
ghenv.Component.NickName = 'FacesByBC'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '2 :: Organize'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
    from honeybee.door import Door
    from honeybee.boundarycondition import Outdoors, Surface, Ground
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee.boundarycondition import Adiabatic
except ImportError:  # honeybee-energy is not installed
    Adiabatic = None  # don't worry about the Adiabatic bc


def add_face(face, geo_list):
    geo_list.append(face)
    for ap in face.apertures:
        geo_list.append(ap)
    for dr in face.doors:
        geo_list.append(dr)



if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    outdoors = []
    surface = []
    ground = []
    adiabatic = []
    other = []

    def sort_face(face):
        bc = face.boundary_condition
        if isinstance(bc, Outdoors):
            add_face(face, outdoors)
        elif isinstance(bc, Surface):
            add_face(face, surface)
        elif isinstance(bc, Ground):
            add_face(face, ground)
        elif isinstance(bc, Adiabatic):
            add_face(face, adiabatic)
        else:
            add_face(face, other)

    def sort_subface(face):
        bc = face.boundary_condition
        if isinstance(bc, Outdoors):
            outdoors.append(face)
        elif isinstance(bc, Surface):
            surface.append(face)
        elif isinstance(bc, Ground):
            ground.append(face)
        elif isinstance(bc, Adiabatic):
            adiabatic.append(face)
        else:
            other.append(face)

    # loop through all objects and add them
    for obj in _hb_objs:
        if isinstance(obj, Model):
            for room in obj.rooms:
                for face in room.faces:
                    sort_face(face)
            for face in obj.orphaned_faces:
                sort_face(face)
            for ap in obj.orphaned_apertures:
                sort_subface(ap)
            for dr in obj.orphaned_doors:
                sort_subface(dr)
        elif isinstance(obj, Room):
            for face in obj:
                sort_face(face)
        elif isinstance(obj, Face):
            sort_face(obj)
        elif isinstance(obj, Aperture):
            sort_subface(obj)
        elif isinstance(obj, Door):
            sort_subface(obj)
