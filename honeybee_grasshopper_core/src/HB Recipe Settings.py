# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Specify settings for the run of a recipe, including the number of workers/CPUs,
the project folder, and other settings.

-
    Args:
        _folder_: Path to a project folder in which the recipe will be executed.
            If None, the default project folder for the Recipe will be used.
        _workers_: An integer to set the number of CPUs used in the execution of the
            recipe. This number should not exceed the number of CPUs on the
            machine and should be lower if other tasks are running while the
            simulation is running. If unspecified, it will automatically default
            to one less than the number of CPUs currently available on the
            machine. (Default: None)
        reload_old_: A boolean to indicate whether existing results for a given
            model and recipe should be reloaded (if they are found) instead of
            re-running the entire recipe from the beginning. If False or
            None, any existing results will be overwritten by the new simulation.
        report_out_: A boolean to indicate whether the recipe progress should be
            displayed in the cmd window (False) or output form the "report" of
            the recipe component (True). Outputting from the component can be
            useful for debugging but recipe reports can often be very long
            and so it can slow Grasshopper slightly. (Default: False).

    Returns:
        settings: Recipe settings that can be plugged into any recipe component to
            specify how the simulation should be run.
"""

ghenv.Component.Name = 'HB Recipe Settings'
ghenv.Component.NickName = 'RecipeSettings'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '7'


try:
    from lbt_recipes.settings import RecipeSettings
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))


# create the settings
settings = RecipeSettings(_folder_, _workers_, reload_old_, report_out_)
