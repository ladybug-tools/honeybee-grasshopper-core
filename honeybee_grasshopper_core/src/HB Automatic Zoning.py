# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Automatically group rooms with similar properties and use the groups to assign zones.
_
Relevant properties that are used to group Room2Ds into zones include story,
orientation, and (optionally) energy programs.
_
Rooms that share the same zone have a common thermostat in energy simulation.
This can often significnatly reduce simulation time without greatly impacting
energy use results.
-

    Args:
        _rooms: A list of honeybee honeybee Rooms to which zones will be assigned.
            This can also be an entire Honeybee Model. Note that these rooms
            should have adjacencies solved in order for them to be correctly
            zoned based on orientation.
        _orient_count_: A positive integer to set the number of orientation groups to
            use for zoning. For example, setting this to 4 will result
            in zones being established based on the four orientations (North,
            East, South, West). (Default: 8).
        north_: A number between 0 and 360 to set the clockwise north direction in
            degrees. This can also be a vector to set the North. Default is 0
            for the world Y-axis.
        ignore_programs_: Boolean for whether the Programs assigned to the Rooms
            should be ignored during the automatic zoning process in which
            case rooms with different programs can appear in the same
            zone. (Default: False).

    Returns:
        report: Errors, warnings, etc.
        rooms: The input Rooms (or Model) with zones assigned based on the input criteria.
"""

ghenv.Component.Name = 'HB Automatic Zoning'
ghenv.Component.NickName = 'AutoZone'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry2d.pointvector import Vector2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import math


if all_required_inputs(ghenv.Component):
    # duplicate the input
    rooms = [obj.duplicate() for obj in _rooms]
    # extract any rooms from input Models
    in_rooms = []
    for hb_obj in rooms:
        if isinstance(hb_obj, Model):
            in_rooms.extend(hb_obj.rooms)
        else:
            in_rooms.append(hb_obj)

    # process the north_ input
    if north_ is not None:
        try:
            north_vec = to_vector2d(north_)
        except AttributeError:  # north angle instead of vector
            north_vec = Vector2D(0, 1).rotate(-math.radians(float(north_)))
    else:
        north_vec = Vector2D(0, 1)

    # assign default values
    orient_count = 8 if _orient_count_ is None else _orient_count_
    attr_name = 'properties.energy.program_type.display_name' \
        if not ignore_programs_ else None

    # assign stories if the rooms do not already have them
    if any(r.story is None for r in in_rooms):
        min_diff = 2.0 / conversion_to_meters()
        Room.stories_by_floor_height(in_rooms, min_diff)

    # automatically assign zones to the input rooms
    Room.automatically_zone(in_rooms, orient_count, north_vec, attr_name)
