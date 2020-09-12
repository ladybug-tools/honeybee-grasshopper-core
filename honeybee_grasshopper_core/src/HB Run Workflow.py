# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Execute any Queenbee workflow on this machine using queenbee-luigi.

-
    Args:
        _workflow: A Queenbee workflow object generated from any Queenbee
            recipe component.
        _folder_: An optional folder out of which the workflow will be executed.
            NOTE THAT DIRECTORIES INPUT HERE SHOULD NOT HAVE ANY SPACES OR
            UNDERSCORES IN THE FILE PATH.
        _cpu_count_: An integer to set the number of CPUs used in the execution
            of the workflow. This number should not exceed the number of CPUs on
            the machine running the simulation and should be lower if other tasks
            are running while the simulation is running.(Default: 2).
        report_out_: A boolean to indicate whether the workflow progress should be
            displayed in the cmd window (False) or output form the "report" of
            this component (True). Outputting from the component can be useful
            for debugging and capturing what's happening in the process but
            workflow reports can often be very long and so it can slow
            Grasshopper slightly. (Default: False).
        _run: Set to "True" to run the workflow.
    
    Returns:
        report: Reports, errors, warnings, etc.
        results: A list of results output from the workflow.
"""

ghenv.Component.Name = 'HB Run Workflow'
ghenv.Component.NickName = 'RunWorkflow'
ghenv.Component.Message = '0.3.2'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '4 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

import os
import subprocess

try:
    from ladybug.futil import nukedir, preparedir
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_radiance.config import folders as rad_folders
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def sort_results_by_grid(results, grid_names):
    """Sort result files according to the order that they appear in a list of grids."""
    file_dict = {}  # dictionary relating grid name to file name
    for res_file in results:
        grid_name = '.'.join(os.path.basename(res_file).split('.')[:-1])
        file_dict[grid_name] = res_file
    grid_files = []
    for g_name in grid_names:
        try:
            grid_files.append(file_dict[g_name])
        except KeyError:  # grid that was not simulated
            pass
    other_files = [val for key, val in file_dict.items() if key not in grid_names]
    return other_files + grid_files


if all_required_inputs(ghenv.Component) and _run:
    # set default number of CPUs
    _cpu_count_ = '2' if not _cpu_count_ else str(_cpu_count_)

    # get the folder out of which the workflow will be executed
    if _folder_ is None:
        if _workflow.default_simulation_path is not None:
            _folder_ = _workflow.default_simulation_path
        else:  # no default simulation path
            _folder_ = os.path.join(
                hb_folders.default_simulation_folder, 'unnamed_workflow')
    if os.path.isdir(_folder_):
        nukedir(_folder_, rmdir=True)  # delete the folder if it already exists
    else:
        preparedir(_folder_)  # create the directory if it's not there

    # write the inputs JSON for the workflow
    inputs_json = _workflow.write_inputs_json(_folder_)

    # execute the queenbee luigi CLI to obtain the results via CPython
    queenbee_exe = os.path.join(hb_folders.python_scripts_path, 'queenbee.exe') \
        if os.name == 'nt' else os.path.join(hb_folders.python_scripts_path, 'queenbee')
    cmds = [queenbee_exe, 'luigi', 'translate', _workflow.path, _folder_,
            '-i', inputs_json, '--workers', _cpu_count_]
    if rad_folders.radlib_path:  # set the RAYPATH environment variable
        cmds.extend(['--env', 'RAYPATH={}'.format(rad_folders.radlib_path)])
    if rad_folders.radbin_path:  # set the PATH environment variable
        cmds.extend(['--env', 'PATH={}'.format(rad_folders.radbin_path)])
    cmds.append('--run')

    if report_out_:
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = process.communicate()
        print result[0]
        print result[1]
    else:
        process = subprocess.Popen(cmds)
        result = process.communicate()

    # try to parse the results
    if _workflow.simulation_id:
        res_folder = os.path.join(_folder_, _workflow.simulation_id, 'results')
        if os.path.isdir(res_folder):
            results = [os.path.join(res_folder, fn) for fn in os.listdir(res_folder)]
            grid_studies = ('annual-daylight', 'daylight-factor')
            if 'sensor-grids' in _workflow.inputs_dict and _workflow.name in grid_studies:
                results = sort_results_by_grid(results, _workflow.inputs_dict['sensor-grids'])
