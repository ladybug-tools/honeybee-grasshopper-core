# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Separate and group honeybee Rooms by any attribute that the room possesses.
_
This can be used to group rooms by program, whether rooms are conditioned, etc.
-

    Args:
        _rooms: An array of honeybee Rooms or honeybee Models to be separated
            and grouped based on their attributes.
        _attribute: Text for the name of the Room attribute with which the
            Rooms should be labeled. The Honeybee "Room Attributes" component
            lists all of the core attributes of the room. Also, each Honeybee
            extension (ie. Radiance, Energy) includes its own component that
            lists the Room attributes of that extension.
    
    Returns:
        values: A list of values with one attribute value for each branch of the
            output rooms.
         rooms: A data tree of honeybee rooms with each branch of the tree
            representing a different attribute value.
"""

ghenv.Component.Name = "HB Rooms by Attribute"
ghenv.Component.NickName = 'RoomsByAttr'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '2 :: Organize'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.colorobj import ColorRoom
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    
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

    # use the ColorRoom object to get a set of attributes assigned to the rooms
    color_obj = ColorRoom(in_rooms, _attribute)
    values = color_obj.attributes_unique

    # loop through each of the rooms and get the attributes
    rooms = [[] for val in values]
    for atr, room in zip(color_obj.attributes, in_rooms):
        atr_i = values.index(atr)
        rooms[atr_i].append(room)
    rooms = list_to_data_tree(rooms)
