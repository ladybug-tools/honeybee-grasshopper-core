# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Set the boundary conditions of Rooms to be Ground vs. Outdoors using a surface or
polysurface that represents the ground.
_
Room faces that are coplanar with the ground surface or have a center below it
will get a Ground boundary condition. Existing Faces with a Surface/Adiabatic
condition, AirBoundary type, or assigned Apertures/Doors will be unaffected.
_
Note that this component will not intersect the Faces with the ground surface and
this is intersection should be done prior to the creation of the Honeybee Rooms.
-

    Args:
        _rooms: Honeybee Rooms which will have their Face boundary conditions set
            based on their spatial relation to the _ground geometry below.
        _ground: Rhino Breps or Meshes that represent the Ground.

    Returns:
        rooms: The input Rooms with their Ground boundary conditions set.
"""

ghenv.Component.Name = 'HB Custom Ground'
ghenv.Component.NickName = 'CustomGround'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance, angle_tolerance
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    rooms = [room.duplicate() for room in _rooms]  # duplicate to avoid editing input
    ground_faces = [g for geo in _ground for g in to_face3d(geo)]  # convert to lb geometry

    # loop through the rooms and set the ground boundary conditions
    for room in rooms:
        room.ground_by_custom_surface(ground_faces, tolerance, angle_tolerance)
