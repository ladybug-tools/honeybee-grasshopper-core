# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Dump any honeybee object to a JSON file. You can use "HB Load Objects" component
to load the objects from the file back into Grasshopper.
-
Honeybee objects include any honeybee energy Material, Construction,
ConstructionSet, Schedule, Load, ProgramType, or Simulation object.
-

    Args:
        _hb_objs: A list of Honeybee objects to be written to a file.
        _name_: A name for the file to which the honeybee objects will be
            written. (Default: 'unnamed').
        _folder_: An optional directory into which the honeybee objects will be
            written.  The default is set to the default simulation folder.
        indent_: An optional positive integer to set the indentation used in the
            resulting JSON file.
        abridged_: Set to "True" to serialize the object in its abridged form.
            Abridged objects cannot be reserialized back to honeybee objects
            on their own but they are used throughout honeybee to minimize
            file size and unnecessary duplication.
        _dump: Set to "True" to save the honeybee objects to file.

    Returns:
        report: Errors, warnings, etc.
        hb_file: The location of the file where the honeybee JSON is saved.
"""

ghenv.Component.Name = 'HB Dump Objects'
ghenv.Component.NickName = 'DumpObjects'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '3 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

import os
import json

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.aperture import Aperture
    from honeybee.door import Door
    from honeybee.shade import Shade
    from honeybee.config import folders
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


if all_required_inputs(ghenv.Component) and _dump:
    # set the component defaults
    name = _name_ if _name_ is not None else 'unnamed'
    file_name = '{}.json'.format(name) if len(_hb_objs) > 1 or not \
        isinstance(_hb_objs[0], Model) else '{}.hbjson'.format(name)
    folder = _folder_ if _folder_ is not None else folders.default_simulation_folder
    hb_file = os.path.join(folder, file_name)
    abridged = bool(abridged_)

    # check to see if any objects are of the geometry type and give a warning
    geo_types = (Room, Face, Aperture, Door, Shade)
    for obj in _hb_objs:
        if isinstance(obj, geo_types):
            geo_object_warning(obj)

    # create the dictionary to be written to a JSON file
    if len(_hb_objs) == 1:  # write a single object into a file if the length is 1
        try:
            obj_dict = _hb_objs[0].to_dict(abridged=abridged)
        except TypeError:  # no abridged option
            obj_dict = _hb_objs[0].to_dict()
    else:  # create a dictionary of the objects that are indexed by name
        obj_dict = {}
        for obj in _hb_objs:
            try:
                obj_dict[obj.identifier] = obj.to_dict(abridged=abridged)
            except TypeError:  # no abridged option
                obj_dict[obj.identifier] = obj.to_dict()

    # write the dictionary into a file
    if not os.path.isdir(folder):
        os.makedirs(folder)
    try:
        with open(hb_file, 'w') as fp:
            json.dump(obj_dict, fp, indent=indent_)
    except UnicodeDecodeError:  # non-unicode character in display_name
        with open(hb_file, 'w') as fp:
            json.dump(obj_dict, fp, indent=indent_, ensure_ascii=False)
