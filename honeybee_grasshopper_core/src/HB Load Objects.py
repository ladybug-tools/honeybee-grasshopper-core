# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Load any honeybee object from a honeybee JSON file
-
Honeybee objects include any Model, Room, Face, Aperture, Door, Shade, or
boundary condition object.
-
It also includes any honeybee energy Material, Construction, ConstructionSet,
Schedule, Load, ProgramType, or Simulation object.
-

    Args:
        _hb_file: A file path to a honeybee JSON from which objects will be loaded
            back into Grasshopper. The objects in the file must be non-abridged
            in order to be loaded back correctly.
        _load: Set to "True to load the objects from the _hb_file.
    
    Returns:
        hb_objs: A list of honeybee objects that have been re-serialized from
            the input file.
"""

ghenv.Component.Name = 'HB Load Objects'
ghenv.Component.NickName = 'LoadObjects'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '3 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:  # import the core honeybee dependencies
    import honeybee.dictutil as hb_dict_util
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core honeybee_energy dependencies
    import honeybee_energy.dictutil as energy_dict_util
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import json


if all_required_inputs(ghenv.Component) and _load:
    with open(_hb_file) as json_file:
        data = json.load(json_file)

    try:
        hb_objs = hb_dict_util.dict_to_object(data, False)  # re-serialize as a core object
        if hb_objs is None:  # try to re-serialize it as an energy object
            hb_objs = energy_dict_util.dict_to_object(hb_dict, False)
    except ValueError:  # no 'type' key; assume that its a group of objects
        hb_objs = []
        for hb_dict in data.values():
            hb_obj = hb_dict_util.dict_to_object(hb_dict, False)  # re-serialize as a core object
            if hb_obj is None:  # try to re-serialize it as an energy object
                hb_obj = energy_dict_util.dict_to_object(hb_dict, False)
            hb_objs.append(hb_obj)