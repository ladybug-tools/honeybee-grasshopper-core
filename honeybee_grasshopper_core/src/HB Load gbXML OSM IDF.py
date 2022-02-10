# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Load a gbXML, OSM, or IDF file as a Honeybee Model.
_
The reverse translators within the OpenStudio SDK are used to import all geometry
and boundary conditions (including adjacencies) to a Honeybee format.
_
Note that, while all geometry will be imported, it is possible that not all of the
properties assigned to this geometry will be imported, particularly if a certain
property is not supported in the OpenStudio SDK. Honeybee will assign defaults
for missing properites and, the HBJSON format should be used whenever lossless
file transfer is needed.
-

    Args:
        _model_file: A file path to a gbXML, OSM or IDF file from which a Honeybee Model
            will be loaded
        _load: Set to "True" to load the Model from the input file.

    Returns:
        model: A honeybee Model objects that has been re-serialized from the input file.
"""

ghenv.Component.Name = 'HB Load gbXML OSM IDF'
ghenv.Component.NickName = 'LoadEModel'
ghenv.Component.Message = '1.4.1'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '3 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

import os
import subprocess
import json

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d.pointvector import Vector3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.result.osw import OSW
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from lbt_recipes.version import check_openstudio_version
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
    from ladybug_rhino.config import conversion_to_meters, units_system, \
        tolerance, angle_tolerance
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


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


if all_required_inputs(ghenv.Component) and _load:
    # check the presence of openstudio and check that the version is compatible
    check_openstudio_version()

    # sense the type of file we are loading
    lower_fname = os.path.basename(_model_file).lower()
    if lower_fname.endswith('.xml') or lower_fname.endswith('.gbxml'):
        cmd_name = 'model-from-gbxml'
        f_name = lower_fname.replace('.gbxml', '.hbjson').replace('.xml', '.hbjson')
    elif lower_fname.endswith('.osm'):
        cmd_name = 'model-from-osm'
        f_name = lower_fname.replace('.osm', '.hbjson')
    elif lower_fname.endswith('.idf'):
        cmd_name = 'model-from-idf'
        f_name = lower_fname.replace('.idf', '.hbjson')
    else:
        raise ValueError('Failed to recongize the input _model_file file type.\n'
                         'Make sure that it has an appropriate file extension.')

    # Execute the honybee CLI to obtain the model JSON via CPython
    out_path = os.path.join(folders.default_simulation_folder, f_name)
    if os.path.isfile(out_path):
        os.remove(out_path)
    cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'translate',
            cmd_name, _model_file, '--output-file', out_path]
    shell = True if os.name == 'nt' else False
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
    result = process.communicate()

    # check to see if the file was successfully output and, if not, report the error
    if not os.path.isfile(out_path):
        osw_path = os.path.join(folders.default_simulation_folder, 'temp_translate', 'out.osw')
        if os.path.isfile(osw_path):
            log_osw = OSW(osw_path)
            print(log_osw.stdout)
            errors = []
            for error, tb in zip(log_osw.errors, log_osw.error_tracebacks):
                print(tb)
                errors.append(error)
            raise Exception('Failed to run OpenStudio CLI:\n{}'.format('\n'.join(errors)))
    
    # if it's all good, load the model and convert it to Rhino model units
    with open(out_path) as json_file:
        model_dict = json.load(json_file)
    model = Model.from_dict(model_dict)
    model_units_tolerance_check(model)

    # given that most other software lets doors go to the edge, move them slightly for HB
    move_vec = Vector3D(0, 0, 0.02 / conversion_to_meters())
    for room in model.rooms:
        for face in room.faces:
            doors = face.doors
            for door in doors:
                if not face.geometry.is_sub_face(door.geometry, tolerance, angle_tolerance):
                    door.move(move_vec)
            if len(doors) != 0:
                face._punched_geometry = None
