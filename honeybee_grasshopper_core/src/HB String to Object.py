# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Serialize any honeybee JSON text string back to a honeybee object.
-
Honeybee objects include any Model, Room, Face, Aperture, Door, Shade, or
boundary condition object.
-
It also includes any honeybee energy Material, Construction, ConstructionSet,
Schedule, Load, ProgramType, or Simulation object.
-

    Args:
        _hb_str: A text string that completely describes the honeybee object.
    
    Returns:
        hb_obj: A Honeybee object serialized from the input string.
"""

ghenv.Component.Name = 'HB String to Object'
ghenv.Component.NickName = 'StrToObj'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '3 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

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


if all_required_inputs(ghenv.Component):
    hb_dict = json.loads(_hb_str)
    hb_obj = hb_dict_util.dict_to_object(hb_dict, False)  # re-serialize as a core object
    if hb_obj is None:  # try to re-serialize it as an energy object
        hb_obj = energy_dict_util.dict_to_object(hb_dict, False)
