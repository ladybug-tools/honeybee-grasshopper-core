# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Serialize any honeybee object to a JSON text string. You can use "HB String to Object"
component to load the objects from the file back.
-
Honeybee objects include any Model, Room, Face, Aperture, Door, Shade, or
boundary condition object.
-
It also includes any honeybee energy Material, Construction, ConstructionSet,
Schedule, Load, ProgramType, or Simulation object.
-

    Args:
        _hb_obj: A Honeybee object to be serialized to a string.
    
    Returns:
        hb_str: A text string that completely describes the honeybee object.
            This can be serialized back into a honeybee object using the "HB
            String to Object" coponent.
"""

ghenv.Component.Name = 'HB Object to String'
ghenv.Component.NickName = 'ObjToStr'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '3 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import json


if all_required_inputs(ghenv.Component):
    hb_str = json.dumps(_hb_obj.to_dict(), indent=4)
