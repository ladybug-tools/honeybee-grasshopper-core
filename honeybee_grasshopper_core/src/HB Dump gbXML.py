# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
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
ghenv.Component.Message = '1.6.2'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '3 :: Serialize'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

import sys
import os
import json

try:  # import the core honeybee dependencies
    from honeybee.model import Model
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee_energy dependencies
    from honeybee_energy.result.osw import OSW
    from honeybee_energy.run import to_gbxml_osw, run_osw, add_gbxml_space_boundaries
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

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

    # duplicate model to avoid mutating it as we edit it for energy simulation
    _model = _model.duplicate()
    # scale the model if the units are not meters
    _model.convert_to_units('Meters')
    # remove degenerate geometry within native E+ tolerance of 1 cm
    _model.remove_degenerate_geometry(0.01)

    # write out the HBJSON and OpenStudio Workflow (OSW) that translates models to gbXML
    out_directory = os.path.join(folders.default_simulation_folder, 'temp_translate')
    if not os.path.isdir(out_directory):
        os.makedirs(out_directory)
    triangulate_ = False if triangulate_ is None else triangulate_
    model_dict = _model.to_dict(included_prop=['energy'], triangulate_sub_faces=triangulate_)
    _model.properties.energy.add_autocal_properties_to_dict(model_dict)
    _model.properties.energy.simplify_window_constructions_in_dict(model_dict)
    hb_file = os.path.join(out_directory, '{}.hbjson'.format(_model.identifier))
    if (sys.version_info < (3, 0)):  # we need to manually encode it as UTF-8
        with open(hb_file, 'wb') as fp:
            obj_str = json.dumps(model_dict, indent=4, ensure_ascii=False)
            fp.write(obj_str.encode('utf-8'))
    else:
        with open(hb_file, 'w', encoding='utf-8') as fp:
            obj_str = json.dump(model_dict, fp, indent=4, ensure_ascii=False)
    osw = to_gbxml_osw(hb_file, gbxml, out_directory)

    # run the measure to translate the model JSON to an openstudio measure
    osm, idf = run_osw(osw, silent=True)
    if idf is None:
        log_osw = OSW(os.path.join(out_directory, 'out.osw'))
        raise Exception(
            'Failed to run OpenStudio CLI:\n{}'.format('\n'.join(log_osw.errors)))

    # add in the space boundary geometry if the user has requested it
    if full_geo_:
        add_gbxml_space_boundaries(gbxml, _model)
