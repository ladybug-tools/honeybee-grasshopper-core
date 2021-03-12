# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Specify settings for the run of a recipe, including the number of workers/CPUs,
the project folder, and other settings.

-
    Args:
        _folder_: Path to a project folder in which the recipe will be executed.
            If None, the default project folder for the Recipe will be used.
        _workers_: An integer to set the number of CPUs used in the execution of the
            recipe. This number should not exceed the number of CPUs on the
            machine running the simulation and should be lower if other tasks
            are running while the simulation is running. (Default: 2).
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
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '7'


try:
    from lbt_recipes.settings import RecipeSettings
except ImportError as e:
    raise ImportError('\nFailed to import lbt_recipes:\n\t{}'.format(e))


# create the settings
_workers_ = 2 if _workers_ is None else _workers_
settings = RecipeSettings(_folder_, _workers_, reload_old_, report_out_)
