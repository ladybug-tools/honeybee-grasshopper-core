# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Take a list of Honeybee Rooms closed breps (polysurfaces) and split their Faces
to ensure that there are matching coplanar faces between them.
_
This matching between Room faces is required in order to contruct a correct
multi-room energy model since conductive heat flow won't occur correctly across
interior faces when their surface areas do not match.
-

    Args:
        _rooms: A list of Honeybee Rooms or closed Rhino breps (polysurfaces) that
            do not have matching adjacent Faces.
        _cpu_count_: An integer to set the number of CPUs used in the execution of the
            intersection calculation. If unspecified, it will automatically default
            to one less than the number of CPUs currently available on the
            machine or 1 if only one processor is available.
        _run: Set to True to run the component.

    Returns:
        int_rooms: The same input Rooms or closed breps that have had their component
            faces split by adjacent geometries to have matching surfaces.
"""

ghenv.Component.Name = 'HB Intersect Solids'
ghenv.Component.NickName = 'IntSolid'
ghenv.Component.Message = '1.6.1'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '2'


try:  # import the honeybee dependencies
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.intersect import bounding_box, intersect_solids, \
        intersect_solids_parallel
    from ladybug_rhino.config import tolerance, angle_tolerance
    from ladybug_rhino.grasshopper import all_required_inputs, \
        recommended_processor_count, run_function_in_parallel
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))



if all_required_inputs(ghenv.Component) and _run:
    # get the number of CPUs to use
    workers = _cpu_count_ if _cpu_count_ is not None else recommended_processor_count()

    if isinstance(_rooms[0], Room):
        # assume that all inputs are Honeybee Rooms
        int_rooms = [room.duplicate() for room in _rooms]
        if workers <= 1:
            Room.intersect_adjacency(int_rooms, tolerance, angle_tolerance)
        else:
            room_geos = [r.geometry for r in int_rooms]
            def intersect_room(r_count):
                rel_room = int_rooms[r_count]
                other_rooms = room_geos[:r_count] + room_geos[r_count + 1:]
                rel_room.coplanar_split(other_rooms, tolerance, angle_tolerance)
            run_function_in_parallel(intersect_room, len(room_geos), workers)
    else:
        # assume that all inputs are closed Rhino Breps
        b_boxes = [bounding_box(brep) for brep in _rooms]
        if workers > 1:
            int_rooms = intersect_solids_parallel(_rooms, b_boxes, workers)
        else:  # just use the single-core process
            int_rooms = intersect_solids(_rooms, b_boxes)
