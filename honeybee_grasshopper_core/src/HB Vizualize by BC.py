# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Visualize room geometry in the Rhino scene organized by boundary condition.
-

    Args:
        _rooms: Honeybee Rooms for which you would like to preview geometry
            in the Rhino scene based on boundary condition. This can also be an
            entire honeybee Model.
    
    Returns:
        outdoors: Rhino geometry for the faces with an Outdoors boundary condition.
        surface: Rhino geometry for the faces with a Surface (interior) boundary
            condition.
        ground: Rhino geometry for the faces with a Ground boundary condition.
        adiabatic: Rhino geometry for the faces with an adiabatic (no heat flow)
            boundary condition.
        other: Rhino geometry for all faces with a boundary condition other than
            the four above.
        wire_frame: A list of lines representing the outlines of the rooms.
"""

ghenv.Component.Name = "HB Vizualize by BC"
ghenv.Component.NickName = 'VizByBC'
ghenv.Component.Message = '0.2.1'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

try:  # import the ladybug dependencies
    from ladybug.color import Colorset
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
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


def add_face(face, geo_list):
    geo_list.append(face.punched_geometry)
    for ap in face.apertures:
        geo_list.append(ap.geometry)
    for dr in face.doors:
        geo_list.append(dr.geometry)


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    _outdoors = []
    _surface = []
    _ground = []
    _adiabatic = []
    _other = []

    # extract any rooms from input Models
    rooms = []
    for hb_obj in _rooms:
        if isinstance(hb_obj, Model):
            rooms.extend(hb_obj.rooms)
        else:
            rooms.append(hb_obj)

    # loop through all objects and add them
    for room in rooms:
        for face in room:
            bc = face.boundary_condition
            if isinstance(bc, Outdoors):
                add_face(face, _outdoors)
            elif isinstance(bc, Surface):
                add_face(face, _surface)
            elif isinstance(bc, Ground):
                add_face(face, _ground)
            elif isinstance(bc, Adiabatic):
                add_face(face, _adiabatic)
            else:
                add_face(face, _other)

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
    other = from_face3ds_to_colored_mesh(_other, palette[9]) \
        if len(_other) != 0 else None

    # create the wire frame
    all_geo = _outdoors + _surface + _ground + _adiabatic + _other
    wire_frame = [from_face3d_to_wireframe(face) for face in all_geo]
