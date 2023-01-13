# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Check the versions of the engines that are being used by the honeybee plugin.
This is useful for verifying that everything has been installed correctly
and that the versions of the engines are as expected.
-

    Returns:
        lbt_gh: The version of Ladybug Tools for Grasshopper that is installed.
        python: The version of Python used for Ladybug Tools CLI calls.
        radiance: The version of Radiance used by Ladybug Tools (will be None if
            it is not installed).
        openstudio: The version of OpenStudio used by Ladybug Tools (will be None if
            it is not installed).
        energyplus: The version of EnergyPlus used by Ladybug Tools (will be None if
            it is not installed).
"""

ghenv.Component.Name = 'HB Check Versions'
ghenv.Component.NickName = 'Versions'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import folders as lbr_folders
    lbr_loaded = True
except ImportError as e:
    lbr_loaded = False

try:
    from honeybee_radiance.config import folders as radiance_folders
    radiance_loaded = True
except ImportError as e:
    radiance_loaded = False

try:
    from honeybee_energy.config import folders as energy_folders
    energy_loaded = True
except ImportError:
    energy_loaded = False


# output the versions
python = hb_folders.python_version_str
if lbr_loaded:
    lbt_gh = lbr_folders.lbt_grasshopper_version_str
if radiance_loaded:
    radiance = radiance_folders.radiance_version_str
if energy_loaded:
    openstudio = energy_folders.openstudio_version_str
    energyplus = energy_folders.energyplus_version_str
