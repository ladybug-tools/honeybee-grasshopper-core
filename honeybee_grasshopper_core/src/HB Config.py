# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Check the local configuration of the engines and data sets used by the honeybee
plugin. This is useful for verifying that everything has been installed correctly
and that the engines are configured as expected.
-

    Returns:
        python_exe: The path to the Python executable to be used for Ladybug
            Tools CLI calls.
        py_lib_install: The path to where the Ladybug Tools Python packages
            are installed.
        rad_install: The path to Radiance installation folder if it exists.
        os_install: The path to OpenStudio installation folder if it exists.
        ep_install: The path to EnergyPlus installation folder if it exists.
        hb_os_gem: The path to the honeybee_openstudio_gem if it exists. This gem
            contains libraries and measures for translating between Honeybee
            JSON schema and OpenStudio Model schema (OSM).
        standards: The path to the library of standards if it exists. This library
            contains the default Modifiers, ModifierSets, Constructions,
            ConstructionSets, Schedules, and ProgramTypes. It can be extended
            by dropping IDF or Honeybee JOSN files into the appropriate sub-folder.
        asset_report: A report of all the assets that have been loaded from the
            standards library.
        default_sim: The path to the default simulation folder (where simulation
            files are written if not specified by the user.).
"""

ghenv.Component.Name = 'HB Config'
ghenv.Component.NickName = 'Config'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_radiance.config import folders as radiance_folders
    from honeybee_radiance.lib.modifiers import MODIFIERS
    from honeybee_radiance.lib.modifiersets import MODIFIER_SETS
    radiance_loaded = True
except ImportError as e:
    radiance_loaded = False

try:
    from honeybee_energy.config import folders as energy_folders
    from honeybee_energy.lib.materials import OPAQUE_MATERIALS
    from honeybee_energy.lib.materials import WINDOW_MATERIALS
    from honeybee_energy.lib.constructions import OPAQUE_CONSTRUCTIONS
    from honeybee_energy.lib.constructions import WINDOW_CONSTRUCTIONS
    from honeybee_energy.lib.constructions import SHADE_CONSTRUCTIONS
    from honeybee_energy.lib.constructionsets import CONSTRUCTION_SETS
    from honeybee_energy.lib.scheduletypelimits import SCHEDULE_TYPE_LIMITS
    from honeybee_energy.lib.schedules import SCHEDULES
    from honeybee_energy.lib.programtypes import PROGRAM_TYPES
    energy_loaded = True
except ImportError:
    energy_loaded = False


# output the paths to the honeybee core folders
report_strs = []
python_exe = hb_folders.python_exe_path
py_lib_install = hb_folders.python_package_path
default_sim = hb_folders.default_simulation_folder


if radiance_loaded:  # output all of the paths to radiance_folders
    rad_install = radiance_folders.radiance_path
    standards = radiance_folders.standards_data_folder

    # generate a report of all the resources loaded from the library
    report_strs.append('{} modifiers loaded'.format(len(MODIFIERS)))
    report_strs.append('{} modifier sets loaded'.format(len(MODIFIER_SETS)))


if energy_loaded:  # output all of the paths to energy_folders
    os_install = energy_folders.openstudio_path
    ep_install = energy_folders.energyplus_path
    hb_os_gem = energy_folders.honeybee_openstudio_gem_path
    standards = energy_folders.standards_data_folder

    # generate a report of all the resources loaded from the library
    report_strs.append('{} opaque materials loaded'.format(len(OPAQUE_MATERIALS)))
    report_strs.append('{} window materials loaded'.format(len(WINDOW_MATERIALS)))
    report_strs.append('{} opaque counstructions loaded'.format(len(OPAQUE_CONSTRUCTIONS)))
    report_strs.append('{} window counstructions loaded'.format(len(WINDOW_CONSTRUCTIONS)))
    report_strs.append('{} shade counstructions loaded'.format(len(SHADE_CONSTRUCTIONS)))
    report_strs.append('{} construction sets loaded'.format(len(CONSTRUCTION_SETS)))
    report_strs.append('{} schedule types loaded'.format(len(SCHEDULE_TYPE_LIMITS)))
    report_strs.append('{} schedules loaded'.format(len(SCHEDULES)))
    report_strs.append('{} program types loaded'.format(len(PROGRAM_TYPES)))

asset_report = '\n'.join(report_strs)
