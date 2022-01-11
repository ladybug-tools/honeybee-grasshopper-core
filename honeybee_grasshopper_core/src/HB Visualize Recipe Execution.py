# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Launch a browser window that can be used to visualize the execution and logs of
any currently-running recipe.
_
Note that this component will only open the recipe visualizer in the default browser
and the page must be refreshed after starting a recipe run in order for the latest
recipe execution status to be visible.
_
Also note that the "Let [RECIPE NAME] Fly" task contains all of the information
about a given recipe run. Selecting "View Graph" for this task and then un-checking
"Hide Done" will allow one to see the full progress of the recipe.

-
    Args:
        _launch: Set to True to run the component and launch a browser window that
            visualizes recipe execution steps.

    Returns:
        report: Reports, errors, warnings, etc.
"""

ghenv.Component.Name = 'HB Visualize Recipe Execution'
ghenv.Component.NickName = 'VizRecipe'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '7'

import os
import subprocess
import webbrowser as wb

try:
    from honeybee.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _launch:
    # set up and run the command to launch the luigi deamon
    ld_path = os.path.join(folders.python_scripts_path, 'luigid')
    process = subprocess.Popen(ld_path, shell=True)

    # open the localhost URL where the recipe will be reported
    local_url = 'http://localhost:8082/'
    try:
        wb.open(local_url, 2, True)
    except ValueError:  # we are using an old version of IronPython
        os.system("open \"\" " + url)
    print('Recipe visualization avaolable at:\n{}'.format(local_url))
