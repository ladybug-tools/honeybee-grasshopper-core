# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Upgrade a Model HBJSON file to the currently installed version of the schema.
_
This component can also upgrade to a specific version of the schema but it
cannot downgrade the schema version or change the version of any honeybee
object other than a Model.
_
A full list of honeybee-schema versions can be found on the honeybee-schema GitHub:
https://github.com/ladybug-tools/honeybee-schema/releases
-

    Args:
        _hbjson: A file path to a Model HBJSON which will be upgraded to the currently
            installed version of the Honeybee Model schema (or a specific version
            specified below).
        version_: Text to indicate the version to which the Model HBJSON will be
            updated (eg. 1.41.2). Versions must always consist of three integers
            separated by periods. If None, the Model HBJSON will be updated to
            the currently installed version of honeybee-schema.
        _name_: A name for the file to which the honeybee objects will be written.
            By default, it will have the same name as the input file but
            with "UPDATED" appended to the file name.
        _folder_: An optional directory into which the updated file will be
            written.  The default is set to the default simulation folder.
        validate_: Boolean to note whether the Honeybee Model should be validated and
            checked for errors after it has been updated. This includes basic
            properties like adjacency and duplicate identifier checks as well
            as geometry checks for planarity, room solidity, etc.
        _update: Set to "True" to update the Model HBJSON to the currently installed
            version.

    Returns:
        report: Reports, errors, warnings, etc.
        hbjson: The file path to the updated HBJSON.
"""

ghenv.Component.Name = 'HB Update HBJSON'
ghenv.Component.NickName = 'UpdateHBJSON'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '3 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os
import subprocess

try:  # import the core honeybee dependencies
    from honeybee.config import folders
    from honeybee.model import Model
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _update:
    # set default variables
    version = version_ if version_ is not None else folders.honeybee_schema_version_str
    name = _name_ if _name_ is not None else \
        os.path.basename(_hbjson).lower().replace('.hbjson', '_UPDATED').replace('.json', '_UPDATED')
    if not (name.endswith('.hbjson') or name.endswith('.json')):
        name = '{}.hbjson'.format(name)
    folder = _folder_ if _folder_ is not None else os.path.dirname(_hbjson)
    hbjson = os.path.join(folder, name)

    # execute the update command and update the HBJSON
    shell = True if os.name == 'nt' else False
    cmds = [folders.python_exe_path, '-m', 'honeybee_schema', 'update-model',
            _hbjson, '--version', version, '--output-file', hbjson]
    process = subprocess.Popen(cmds, stderr=subprocess.PIPE, shell=shell)
    stderr = process.communicate()
    print(stderr[-1])

    # validate the model if validation was requested
    if validate_:
        parsed_model = Model.from_hbjson(hbjson)
        valid_report = parsed_model.check_all(raise_exception=False)
        if valid_report != '':
            print(valid_report)
            give_warning(ghenv.Component, valid_report)
