# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Separate and group honeybee rooms with the same average floor height.
-

    Args:
        _rooms: A list of honeybee Rooms or honeybee Models to be separated by
            floor height.
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
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '2 :: Organize'
ghenv.Component.AdditionalHelpFromDocStrings = '2'


try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models
    in_rooms = []
    for hb_obj in _rooms:
        if isinstance(hb_obj, Model):
            in_rooms.extend(hb_obj.rooms)
        else:
            in_rooms.append(hb_obj)

    # loop through each of the rooms and get the floor height
    grouped_rooms, flr_hgts = Room.group_by_floor_height(in_rooms, tolerance)

    # convert matrix to data tree
    rooms = list_to_data_tree(grouped_rooms)
