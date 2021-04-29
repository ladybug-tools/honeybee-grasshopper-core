# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

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
        _gbxml: A file path to a gbXML, OSM or IDF file from which a Honeybee Model
            will be loaded
        _load: Set to "True" to load the Model from the input file.

    Returns:
        model: A honeybee Model objects that has been re-serialized from the input file.
"""

ghenv.Component.Name = 'HB Load gbXML'
ghenv.Component.NickName = 'LoadGBXML'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '3 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry3d.pointvector import Vector3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
    from ladybug_rhino.config import conversion_to_meters, units_system, tolerance
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

import os
import subprocess
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


if all_required_inputs(ghenv.Component) and _load:
    # sense the type of file we are loading
    lower_fname = _gbxml.lower()
    if lower_fname.endswith('.xml') or lower_fname.endswith('.gbxml'):
        cmd_name = 'model-from-gbxml'
    elif lower_fname.endswith('.osm'):
        cmd_name = 'model-from-osm'
    elif lower_fname.endswith('.idf'):
        cmd_name = 'model-from-idf'
    else:
        raise ValueError('Failed to recongize the input _gbxml file type.\n'
                         'Make sure that it has an appropriate file extension.')

    # Execute the honybee CLI to obtain the model JSON via CPython
    shell = True if os.name == 'nt' else False
    cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'translate',
            cmd_name, _gbxml]
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=shell)
    stdout = process.communicate()
    model_dict = json.loads(stdout[0])

    # load the model from the JSON dictionary and convert it to Rhino model units
    model = Model.from_dict(model_dict)
    model_units_tolerance_check(model)

    # given that most other software lets doors go to the edge, move them slightly for HB
    move_vec = Vector3D(0, 0, 0.02 / conversion_to_meters())
    for room in model.rooms:
        for face in room.faces:
            doors = face.doors
            for door in doors:
                door.move(move_vec)
            if len(doors) != 0:
                face._punched_geometry = None
