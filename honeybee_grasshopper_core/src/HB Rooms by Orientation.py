# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Separate and group honeybee rooms with the same average orientation of walls
with an Outdoors boundary condition.
-

    Args:
        _rooms: A list of honeybee rooms to be separated by orientation.
        n_groups_: An optional positive integer to set the number of orientation
            groups to use. For example, setting this to 4 will result in rooms
            being grouped by four orientations (North, East, South, West). If None,
            the maximum number of unique groups will be used.
        north_: A number between 0 and 360 to set the clockwise north
            direction in degrees. This can also be a vector to set the North.
            Default is 0.

    Returns:
        orientations: A list of numbers between 0 and 360 with one orientation
            for each branch of the output perim_rooms. This will be a list of
            angle ranges if a value is input for n_groups_.
        perim_rooms: A data tree of honeybee rooms with each branch of the tree
            representing a different orientation.
        core_rooms: A list of honeybee rooms with no identifiable orientation.
"""

ghenv.Component.Name = "HB Rooms by Orientation"
ghenv.Component.NickName = 'Orientation'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '2 :: Organize'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry2d.pointvector import Vector2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.orientation import angles_from_num_orient, orient_index
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import math


if all_required_inputs(ghenv.Component):
    # process the north_ input
    if north_ is not None:
        try:
            north_vec = to_vector2d(north_)
        except AttributeError:  # north angle instead of vector
            north_vec = Vector2D(0, 1).rotate(-math.radians(float(north_)))
    else:
        north_vec = Vector2D(0, 1)

    # loop through each of the rooms and get the orientation
    orient_dict = {}
    core_rooms = []
    for room in _rooms:
        ori = room.average_orientation(north_vec)
        if ori is None:
            core_rooms.append(room)
        else:
            try:
                orient_dict[ori].append(room)
            except KeyError:
                orient_dict[ori] = []
                orient_dict[ori].append(room)

    # sort the rooms by orientation values
    room_mtx = sorted(orient_dict.items(), key = lambda d: float(d[0]))
    orientations = [r_tup[0] for r_tup in room_mtx]
    perim_rooms = [r_tup[1] for r_tup in room_mtx]

    # group orientations if there is an input n_groups_
    if n_groups_ is not None:
        angs = angles_from_num_orient(n_groups_)
        p_rooms = [[] for i in range(n_groups_)]
        for ori, rm in zip(orientations, perim_rooms):
            or_ind = orient_index(ori, angs)
            p_rooms[or_ind].extend(rm)
        orientations = ['{} - {}'.format(int(angs[i - 1]), int(angs[i]))
                        for i in range(n_groups_)]
        perim_rooms = p_rooms

    # convert matrix to data tree
    perim_rooms = list_to_data_tree(perim_rooms)
