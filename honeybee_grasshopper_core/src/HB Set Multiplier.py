# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Change the multiplier of a honeybee Room.
_
Multipliers are used to speed up the calculation when similar Rooms are
repeated more than once. Essentially, a given simulation with the
Room is run once and then the result is mutliplied by the multiplier.
This means that the "repetition" isn't in a particualr direction (it's
essentially in the exact same location) and this comes with some
inaccuracy. However, this error might not be too large if the Rooms
are similar enough and it can often be worth it since it can greatly
speed up the calculation.
-

    Args:
        _rooms: Honeybee Rooms to which the input _multipier should be assigned.
        _multiplier: An integer noting how many times the Rooms are repeated.
            This can also be an array of integers, which align with the input
            _rooms and will be matched to them accordingly
    
    Returns:
        report: ...
        rooms: The input Rooms with their multipliers edited.
"""

ghenv.Component.Name = "HB Set Multiplier"
ghenv.Component.NickName = 'Multiplier'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'


try:  # import the honeybee-energy extension
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    rooms = []
    for i, room in enumerate(_rooms):
        assert isinstance(room, Room), \
            'Expected honeybee room. Got {}.'.format(type(room))
        room_dup = room.duplicate()
        room_dup.multiplier = longest_list(_multiplier, i)
        rooms.append(room_dup)
