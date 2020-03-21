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
            in the Rhino scene based on boundary condition.
    
    Returns:
        outdoors: Rhino geometry for the faces with an Outdoors boundary condition.
        surface: Rhino geometry for the faces with a Surface (interior) boundary
            condition.
        ground: Rhino geometry for the faces with a Ground boundary condition.
        adiabatic: Rhino geometry for the faces with an adiabatic (no heat flow)
            boundary condition.
        other: Rhino geometry for all faces with a boundary condition other than
            the four above.
"""

ghenv.Component.Name = "HB Vizualize by BC"
ghenv.Component.NickName = 'VizByBC'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors, Surface, Ground
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.fromgeometry import from_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee.boundarycondition import Adiabatic
except ImportError:  # honeybee-energy is not installed
    Adiabatic = None  # don't worry about the Adiabatic bc


def add_face(face, geo_list):
    geo_list.append(from_face3d(face.punched_geometry))
    for ap in face.apertures:
        geo_list.append(from_face3d(ap.geometry))
    for dr in face.doors:
        geo_list.append(from_face3d(dr.geometry))


if all_required_inputs(ghenv.Component):
    # lists of rhino geometry to be filled with content
    outdoors = []
    surface = []
    ground = []
    adiabatic = []
    other = []
    
    # loop through all objects and add them
    for room in _rooms:
        for face in room:
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