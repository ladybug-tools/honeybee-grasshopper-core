# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get geometry properties of honeybee Rooms or a honeybee Model.
-

    Args:
        _rooms: A list of honeybee Rooms for which or geometry properties will be output.
            This can also be an entire honeybee Model.

    Returns:
        ext_wall_area: A number for the total area of walls in the honeybee rooms
            with an Outdoors boundary condition (in Rhino model units).
        ext_win_area: A number for the total area of windows in the honeybee rooms
            with an Outdoors boundary condition (in Rhino model units).
        volume: A number for the volume of the honeybee rooms (in Rhino model units).
        floor_area: A number for the floor area  of the honeybee rooms (in Rhino
            model units). When a Model is connected, the floor area will exclude
            plenums and other Rooms with that have a True exclude_floor_area
            property.
        floor_ep_constr: A number for the floor area of the Room accounting for the thickness
            of EnergyPlus wall constructions. (in Rhino model units). When a
            Model is connected, the floor area will exclude plenums and other
            Rooms with that have a True exclude_floor_area property.
"""

ghenv.Component.Name = 'HB Geometry Properties'
ghenv.Component.NickName = 'GeoProp'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.config import units_system, tolerance
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # extract any rooms from input Models
    rooms, is_model = [], False
    for hb_obj in _rooms:
        if isinstance(hb_obj, Room):
            rooms.append(hb_obj)
        elif isinstance(hb_obj, Model):
            rooms.extend(hb_obj.rooms)
            is_model = True
        else:
            raise ValueError(
                'Expected Honeybee Room or Model. Got {}.'.format(type(hb_obj)))

    # get the properties that all objects share
    units = units_system()
    if is_model:
        ext_wall_area = sum([r.exterior_wall_area * r.multiplier for r in rooms])
        ext_win_area = sum([r.exterior_aperture_area * r.multiplier for r in rooms])
        volume = sum([r.volume * r.multiplier for r in rooms])
        floor_area = sum([r.floor_area * r.multiplier for r in rooms if not r.exclude_floor_area])
        try:
            floor_ep_constr = \
                sum([r.properties.energy.floor_area_with_constructions(units, units, tolerance) * r.multiplier
                     for r in rooms if not r.exclude_floor_area])
        except AttributeError:
            pass  # honeybee-energy is not installed
    else:
        ext_wall_area = [r.exterior_wall_area for r in rooms]
        ext_win_area = [r.exterior_aperture_area for r in rooms]
        volume = [r.volume for r in rooms]
        floor_area = [r.floor_area for r in rooms]
        try:
            floor_ep_constr = \
                [r.properties.energy.floor_area_with_constructions(units, units, tolerance)
                 for r in rooms]
        except AttributeError:
            pass  # honeybee-energy is not installed
