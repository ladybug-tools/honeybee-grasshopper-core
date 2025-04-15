# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Dump a Honyebee Model to a gbXML file.
_
The gbXML format is a common open standard used to transfer energy model geometry
and (some) energy simulation properties from one simulation environment to another.
_
The forward translators within the OpenStudio SDK are used to export all Honeybee
model geometry and properties.
-

    Args:
        _model: A Honeybee Model object to be written to a gbXML file.
        _name_: A name for the file to which the honeybee objects will be written.
            If unspecified, it will be derived from the model identifier.
        _folder_: An optional directory into which the honeybee objects will be
            written.  The default is set to the default simulation folder.
        int_floors_: A boolean to note whether all interior horizontal faces should
            be written with the InteriorFloor type instead of the combination
            of InteriorFloor and Ceiling that happens by default with OpenStudio
            gbXML serialization. (Default: False).
        triangulate_: Boolean to note whether sub-faces (including Apertures and Doors)
            should be triangulated if they have more than 4 sides (True) or
            whether they should be left as they are (False). This triangulation
            is necessary when exporting directly to EnergyPlus since it cannot
            accept sub-faces with more than 4 vertices. However, it is not a
            general requirement of gbXML or all of the simulation engines that
            gbXML can import to/from. (Default: False).
        full_geo_: Boolean to note whether space boundaries and shell geometry should
            be included in the exported gbXML vs. just the minimal required
            non-manifold geometry. Setting to True to include the full geometry
            will increase file size without adding much new infomration that
            doesn't already exist in the file. However, some gbXML interfaces
            need this geometry in order to properly represent and display
            room volumes. (Default: False).
        _dump: Set to "True" to save the honeybee model to a gbXML file.

    Returns:
        report: Errors, warnings, etc.
        hb_file: The location of the file where the honeybee JSON is saved.
"""

ghenv.Component.Name = 'HB Dump gbXML'
ghenv.Component.NickName = 'DumpGBXML'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '3 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

import os
import json
import subprocess
import tempfile

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_openstudio.writer import model_to_gbxml
except (ImportError, AssertionError):  # openstudio .NET bindings are not available
    model_to_gbxml = None

try:
    from lbt_recipes.version import check_openstudio_version
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _dump:
    # check the presence of openstudio and check that the version is compatible
    check_openstudio_version()

    # check the input and set the component defaults
    assert isinstance(_model, Model), \
        'Excpected Honeybee Model object. Got {}.'.format(type(_model))
    name = _name_ if _name_ is not None else _model.identifier
    lower_name = name.lower()
    gbxml_file = name if lower_name.endswith('.xml') or lower_name.endswith('.gbxml') \
        else '{}.xml'.format(name)
    folder = _folder_ if _folder_ is not None else folders.default_simulation_folder
    gbxml = os.path.join(folder, gbxml_file)
    triangulate_subfaces = True if triangulate_ else False
    full_geometry = True if full_geo_ else False
    interior_face_type = 'InteriorFloor' if int_floors_ else None

    # write the Model to a gbXML file
    if model_to_gbxml is not None:  # run the whole translation in IronPython
        gbxml_str = model_to_gbxml(
            _model, triangulate_subfaces=triangulate_subfaces,
            full_geometry=full_geometry, interior_face_type=interior_face_type
        )
        with open(gbxml, 'w') as outf:
            outf.write(gbxml_str)
    else:  # do the translation using cPython through the CLI
        # write the model to a HBJSON
        temp_dir = tempfile.gettempdir()
        model_file = os.path.join(temp_dir, 'in.hbjson')
        with open(model_file, 'w') as fp:
            model_str = json.dumps(_model.to_dict(), ensure_ascii=False)
            fp.write(model_str.encode('utf-8'))
        # execute the command to convert the HBJSON to gbXML
        cmds = [folders.python_exe_path, '-m', 'honeybee_energy', 'translate',
                'model-to-gbxml', model_file, '--output-file', gbxml]
        if triangulate_subfaces:
            cmds.append('--triangulate-subfaces')
        if full_geometry:
            cmds.append('--full-geometry')
        if int_floors_:
            cmds.append('--interior-face-type')
            cmds.append(interior_face_type)
        custom_env = os.environ.copy()
        custom_env['PYTHONHOME'] = ''
        process = subprocess.Popen(cmds, shell=True, env=custom_env)
        result = process.communicate()  # freeze the canvas while running
