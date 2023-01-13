# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


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
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '3 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:  # import the core honeybee dependencies
    import honeybee.dictutil as hb_dict_util
    from honeybee.model import Model
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core honeybee_energy dependencies
    import honeybee_energy.dictutil as energy_dict_util
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core honeybee_radiance dependencies
    import honeybee_radiance.dictutil as radiance_dict_util
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
    from ladybug_rhino.config import units_system, tolerance
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import json


def model_units_tolerance_check(model):
    """Convert a model to the current Rhino units and check the tolerance.

    Args:
        model: A honeybee Model, which will have its units checked.
    """
    # check the model units
    if model.units != units_system():
        print('Imported model units "{}" do not match that of the current Rhino '
            'model units "{}"\nThe model is being automatically converted '
            'to the Rhino doc units.'.format(model.units, units_system()))
        model.convert_to_units(units_system())

    # check that the model tolerance is not too far from the Rhino tolerance
    if model.tolerance / tolerance >= 100:
        msg = 'Imported Model tolerance "{}" is significantly coarser than the ' \
            'current Rhino model tolerance "{}".\nIt is recommended that the ' \
            'Rhino document tolerance be changed to be coarser and this ' \
            'component is re-run.'.format(model.tolerance, tolerance)
        print msg
        give_warning(ghenv.Component, msg)


def version_check(data):
    """Check the version of the object if it was included in the dictionary.

    This is most useful in cases of importing entire Models to make sure
    the Model isn't newer than the currently installed Honeybee.

    Args:
        data: Dictionary of the object, which optionally has the "version" key.
    """
    if 'version' in data and data['version'] is not None:
        model_ver = tuple(int(d) for d in data['version'].split('.'))
        hb_ver = folders.honeybee_schema_version
        if model_ver > hb_ver:
            msg = 'Imported Model schema version "{}" is newer than that with the ' \
            'currently installed Honeybee "{}".\nThe Model may fail to import ' \
            'or (worse) some newer features of the Model might not be imported ' \
            'without detection.'.format(data['version'], folders.honeybee_schema_version_str)
            print msg
            give_warning(ghenv.Component, msg)
        elif model_ver != hb_ver:
            msg = 'Imported Model schema version "{}" is older than that with the ' \
            'currently installed Honeybee "{}".\nThe Model will be upgraded upon ' \
            'import.'.format(data['version'], folders.honeybee_schema_version_str)
            print msg


if all_required_inputs(ghenv.Component):
    hb_dict = json.loads(_hb_str)
    version_check(hb_dict)  # try to check the version
    hb_obj = hb_dict_util.dict_to_object(hb_dict, False)  # re-serialize as a core object
    if hb_obj is None:  # try to re-serialize it as an energy object
        hb_obj = energy_dict_util.dict_to_object(hb_dict, False)
        if hb_obj is None:  # try to re-serialize it as a radiance object
            hb_obj = radiance_dict_util.dict_to_object(hb_dict, False)
    elif isinstance(hb_obj, Model):
        model_units_tolerance_check(hb_obj)
