# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Execute any Recipe on this machine using queenbee-luigi.

-
    Args:
        _recipe: A recipe object generated from any recipe component.
        _folder_: An optional folder out of which the recipe will be executed.
        _cpu_count_: An integer to set the number of CPUs used in the execution
            of the recipe. This number should not exceed the number of CPUs on
            the machine running the simulation and should be lower if other tasks
            are running while the simulation is running. (Default: 2).
        reload_old_: A boolean to indicate whether existing results for a given
            model and recipe should be reloaded if they are found instead of
            re-running the entire recipe from the beginning. If False or
            None, any existing results will be overwritten by the new simulation.
        report_out_: A boolean to indicate whether the recipe progress should be
            displayed in the cmd window (False) or output form the "report" of
            this component (True). Outputting from the component can be useful
            for debugging and capturing what's happening in the process but
            recipe reports can often be very long and so it can slow
            Grasshopper slightly. (Default: False).
        _run: Set to "True" to run the recipe.

    Returns:
        report: Reports, errors, warnings, etc.
        results: The results output from the recipe.
"""

ghenv.Component.Name = 'HB Run Recipe'
ghenv.Component.NickName = 'RunRecipe'
ghenv.Component.Message = '1.1.3'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '4 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import subprocess

try:
    from ladybug.futil import preparedir, nukedir
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_radiance.config import folders as rad_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning, \
        list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# check the installed Radiance and ensure it's from the right date
compatible_rad_date = (2020, 9, 3)
hb_url = 'https://github.com/ladybug-tools/lbt-grasshopper/wiki/1.4-Compatibility-Matrix'
rad_msg = 'Download and install the version of Radiance listed in the Ladybug ' \
    'Tools compatibility matrix\n{}'.format(hb_url)
assert rad_folders.radiance_path is not None, \
    'No Radiance installation was found on this machine.\n{}'.format(rad_msg)
assert rad_folders.radiance_version_date >= compatible_rad_date, \
    'The installed Radiance is not from {} or later.' \
    '\n{}'.format('/'.join(str(v) for v in compatible_rad_date), rad_msg)


if all_required_inputs(ghenv.Component) and _run:
    # set default number of CPUs
    _cpu_count_ = '2' if not _cpu_count_ else str(_cpu_count_)

    # get the folder out of which the recipe will be executed
    if _folder_ is None:
        _folder_ = _recipe.default_project_folder
    if not os.path.isdir(_folder_):
        preparedir(_folder_)  # create the directory if it's not there

    # delete any existing result files unless reload_old_ is True
    if not reload_old_ and _recipe.simulation_id is not None:
        wf_folder = os.path.join(_folder_, _recipe.simulation_id)
        if os.path.isdir(wf_folder):
            nukedir(wf_folder, rmdir=True)

    # write the inputs JSON for the recipe and set up the envrionment variables
    inputs_json = _recipe.write_inputs_json(_folder_)
    genv = {}
    genv['PATH'] = rad_folders.radbin_path
    genv['RAYPATH'] = rad_folders.radlib_path
    env_args = ['--env {}="{}"'.format(k, v) for k, v in genv.items()]

    # create command
    command = '"{qb_path}" local run "{recipe_folder}" ' \
        '"{project_folder}" -i "{user_inputs}" --workers {cpu_count} ' \
        '{environment} --name {simulation_name}'.format(
            qb_path=os.path.join(hb_folders.python_scripts_path, 'queenbee'),
            recipe_folder=_recipe.path, project_folder=_folder_,
            user_inputs=inputs_json, cpu_count=_cpu_count_,
            environment=' '.join(env_args),
            simulation_name=_recipe.simulation_id
        )

    # execute command
    shell = False if os.name == 'nt' else True
    if report_out_:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
        result = process.communicate()
        print result[0]
        print result[1]
    else:
        process = subprocess.Popen(command, shell=shell)
        result = process.communicate()  # freeze the canvas while running

    # try to parse the results
    try:
        results = _recipe.output_value_by_name('results', _folder_)
        if isinstance(results, (list, tuple)):
            results = list_to_data_tree(results)
    except (AssertionError, ValueError) as e:
        msg = 'Simulation did not succeed. Try setting reoprt_out_ to True to ' \
            'see the full traceback.\n{}'.format(e)
        give_warning(ghenv.Component, msg)
