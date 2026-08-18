# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2026, Ladybug Tools.
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
        ip_units_: A boolean to note whether the geometry, space loads, and
            construction properties are reported in IP units (True) or SI
            units (False). (Default: False).
        full_geo_: Boolean to note whether space boundaries and shell geometry are
            included in the exported gbXML vs. just the minimal required
            non-manifold Surface geometry. Setting to True increases file
            size without adding much new infomration beyond that which is
            already described under the Surface geometry. However, some gbXML
            interfaces need these extra "copies" of the geometry in order to
            properly represent and display room volumes. (Default: False).
        _rect_format_: Text to note how the rectangular geometry for all Surfaces
            is written into the gbXML. BoundingRectangle sets the width
            and height of the rectangular geometry using the bounding
            rectangle around the geometry, which results in an overestimated
            area for non-rectangular geo. SimpleArea will set the rectangle width
            always equal to geometry area and the height always equal to one,
            ensuring accurate areas and making it easy to check the geometry
            area in the gbXML. SimpleAreaForNonRectOnly will report the width and
            height of rectangular Face3D correctly but use simpler areas
            for non-rectangular geometry. (Default: BoundingRectangle). Choose
            from the following.
            * BoundingRectangle
            * SimpleArea
            * SimpleAreaForNonRectOnly
        reset_ids_: Boolean to note whether a cleaned version of geometry display
            names should be used for the IDs that appear within the gbXML file.
            Setting to True will generally result in more read-able IDs in the
            gbXML file but this means that it will not be easy to map results
            back to the input Model. Cases of duplicate IDs resulting from
            non-unique names will be resolved by adding integers to the ends
            of the new IDs that are derived from the name. (Default: False).
        _dump: Set to "True" to save the honeybee model to a gbXML file.

    Returns:
        report: Errors, warnings, etc.
        hb_file: The location of the file where the honeybee JSON is saved.
"""

ghenv.Component.Name = 'HB Dump gbXML'
ghenv.Component.NickName = 'DumpGBXML'
ghenv.Component.Message = '1.10.1'
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
    from honeybee_energy.writer import model_to_gbxml
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.config import folders as lbr_folders
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _dump:
    # check the input model and name zones differently from rooms
    assert isinstance(_model, Model), \
        'Excpected Honeybee Model object. Got {}.'.format(type(_model))
    model = _model.duplicate()
    if bool(reset_ids_):
        model.reset_ids()
    for room in model.rooms:
        if room.zone == room.identifier:
            room.zone = '{} Zone'.format(room.identifier)

    # set the component defaults
    name = _name_ if _name_ is not None else _model.identifier
    lower_name = name.lower()
    gbxml_file = name if lower_name.endswith('.xml') or lower_name.endswith('.gbxml') \
        else '{}.xml'.format(name)
    folder = _folder_ if _folder_ is not None else folders.default_simulation_folder
    gbxml = os.path.join(folder, gbxml_file)
    ip_units = bool(ip_units_)
    full_geo = bool(full_geo_)
    rect_geo_format = 'BoundingRectangle' if _rect_format_ is None else _rect_format_
    prog_name = 'Ladybug Tools for Grasshopper'
    lbt_gh = lbr_folders.lbt_grasshopper_version_str

    # write the Model to a gbXML file
    gbxml_str = model_to_gbxml(
        model, ip_units=ip_units,
        include_shell_geometry=full_geo, include_space_boundaries=full_geo,
        rect_geo_format=rect_geo_format,
        program_name=prog_name, program_version=lbr_folders.lbt_grasshopper_version_str
    )
    gbxml_str = '<?xml version="1.0" encoding="utf-8"?>\n' + gbxml_str
    with open(gbxml, 'w') as outf:
        outf.write(gbxml_str)
