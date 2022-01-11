# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
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
        python: The version of Python used for Ladybug Tools CLI calls.
        radiance: The version of Radiance if it is installed.
        openstudio: The version of OpenStudio if it is installed.
        energyplus: The version of EnergyPlus if it is installed.
"""

ghenv.Component.Name = 'HB Check Versions'
ghenv.Component.NickName = 'Versions'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

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
if radiance_loaded:
    radiance = radiance_folders.radiance_version_str
if energy_loaded:
    openstudio = energy_folders.openstudio_version_str
    energyplus = energy_folders.energyplus_version_str
