# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Serialize any honeybee object to a JSON text string. You can use "HB String to Object"
component to load the objects from the file back.
-
Honeybee objects include any honeybee energy Material, Construction,
ConstructionSet, Schedule, Load, ProgramType, or Simulation object.
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
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '3 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import json

try:  # import the core honeybee dependencies
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
    from honeybee.door import Door
    from honeybee.shade import Shade
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def geo_object_warning(obj):
    """Give a warning that individual geometry objects should be added to a Model."""
    msg = 'An individual {} has been connected to the _hb_objs.\n' \
        'The recommended practice is to add this object to a Model and\n' \
        'serialize the Model instead of serializing individual objects.'.format(
            obj.__class__.__name__)
    print(msg)
    give_warning(ghenv.Component, msg)


if all_required_inputs(ghenv.Component):
    # check to see if any objects are of the geometry type and give a warning
    geo_types = (Room, Face, Aperture, Door, Shade)
    if isinstance(_hb_obj, geo_types):
        geo_object_warning(_hb_obj)
    # serialize the object
    hb_str = json.dumps(_hb_obj.to_dict(), indent=4)
