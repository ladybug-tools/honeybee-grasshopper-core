# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Dump any honeybee object to a compressed .pkl file. You can use "HB Load Compressed
Objects" component to load the objects from the file back into Grasshopper.
-
Honeybee objects include any Model, Room, Face, Aperture, Door, Shade, or
boundary condition object
-
It also includes any honeybee energy Material, Construction, ConstructionSet,
Schedule, Load, ProgramType, or Simulation object.
-

    Args:
        _hb_objs: A Honeybee object (or list of Honeybee objects) to be written
            to a file.
        _name_: A name for the file to which the honeybee objects will be
            written. (Default: 'unnamed').
        _folder_: An optional directory into which the honeybee objects will be
            written.  The default is set to the default simulation folder.
        _dump: Set to "True" to save the honeybee objects to file.

    Returns:
        report: Errors, warnings, etc.
        hb_file: The location of the file where the honeybee .pkl file is saved.
"""

ghenv.Component.Name = 'HB Dump Compressed Objects'
ghenv.Component.NickName = 'DumpCompressed'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '3 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import os
import cPickle as pickle


if all_required_inputs(ghenv.Component) and _dump:
    # set the component defaults
    name = _name_ if _name_ is not None else 'unnamed'
    file_name = '{}.pkl'.format(name) if len(_hb_objs) > 1 or not \
        isinstance(_hb_objs[0], Model) else '{}.hbpkl'.format(name)
    folder = _folder_ if _folder_ is not None else folders.default_simulation_folder
    hb_file = os.path.join(folder, file_name)

    # create the dictionary to be written to a .pkl file
    if len(_hb_objs) == 1:  # write a single object into a file if the length is 1
        obj_dict = _hb_objs[0].to_dict()
    else:  # create a dictionary of the objects that are indexed by name
        obj_dict = {}
        for obj in _hb_objs:
            obj_dict[obj.identifier] = obj.to_dict()

    # write the dictionary into a file
    if not os.path.isdir(folder):
        os.makedirs(folder)
    with open(hb_file, 'wb') as fp:
        pickle.dump(obj_dict, fp)
