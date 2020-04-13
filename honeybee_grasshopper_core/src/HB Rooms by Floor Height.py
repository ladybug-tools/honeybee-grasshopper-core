# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Separate and group honeybee rooms with the same average floor height.
-

    Args:
        _rooms: A list of honeybee rooms to be separated by floor height.
        min_diff_: An optional float value to denote the minimum difference
            in floor heights that is considered meaningful. This can be used
            to ensure rooms like those representing stair landings are grouped
            with floors. If None, any difference in floor heights greater than
            the Rhino model tolerance will be considered meaningful.

    Returns:
        flr_hgts: A list of floor heights with one floor height for each branch
            of the output rooms.
        rooms: A data tree of honeybee rooms with each branch of the tree
            representing a different floor height.
"""


ghenv.Component.Name = "HB Rooms by Floor Height"
ghenv.Component.NickName = 'FloorHeight'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '2 :: Organize'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # loop through each of the rooms and get the floor height
    flrhgt_dict = {}
    for room in _rooms:
        flrhgt = room.average_floor_height
        try:
            flrhgt_dict[flrhgt].append(room)
        except KeyError:
            flrhgt_dict[flrhgt] = []
            flrhgt_dict[flrhgt].append(room)

    # sort the rooms by floor heights
    room_mtx = sorted(flrhgt_dict.items(), key = lambda d: float(d[0]))
    flr_hgts = [r_tup[0] for r_tup in room_mtx]
    rooms = [r_tup[1] for r_tup in room_mtx]

    # group floor heights if they differ by less than the min_diff
    min_diff = tolerance if min_diff_ is None else min_diff_
    new_flr_hgts = [flr_hgts[0]]
    new_rooms = [rooms[0]]
    for flrh, rm in zip(flr_hgts[1:], rooms[1:]):
        if flrh - new_flr_hgts[-1] < min_diff:
            new_rooms[-1].extend(rm)
        else:
            new_rooms.append(rm)
            new_flr_hgts.append(flrh)
    flr_hgts = new_flr_hgts
    rooms = new_rooms

    # convert matrix to data tree
    rooms = list_to_data_tree(rooms)
