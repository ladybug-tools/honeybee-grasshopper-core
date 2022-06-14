# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>


"""
Take a list of closed breps (polysurfaces) and split their Faces to ensure that
there are matching surfaces between them.
_
This matching between Room faces is required in order to contruct a correct
multi-room energy model since conductive heat flow won't occur correctly across
interior faces when their surface areas do not match.
-

    Args:
        _solids: A list of closed Rhino breps (polysurfaces) that do not have matching
            surfaces between adjacent Faces.
        _cpu_count_: An integer to set the number of CPUs used in the execution of the
            intersection calculation. If unspecified, it will automatically default
            to one less than the number of CPUs currently available on the
            machine or 1 if only one processor is available.
        _run: Set to True to run the component.

    Returns:
        int_solids: The same input closed breps that have had their component
            faces split by adjacent polysurfaces to have matching surfaces between
            adjacent breps.  It is recommended that you bake this output and check
            it in Rhino before turning the breps into honeybee Rooms.
"""

ghenv.Component.Name = "HB Intersect Solids"
ghenv.Component.NickName = 'IntSolid'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"


try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.intersect import bounding_box, intersect_solids, \
        intersect_solids_parallel
    from ladybug_rhino.grasshopper import all_required_inputs, recommended_processor_count
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))



if all_required_inputs(ghenv.Component) and _run:
    # generate bounding boxes for all inputs
    b_boxes = [bounding_box(brep) for brep in _solids]

    # intersect all of the solid geometries
    workers = _cpu_count_ if _cpu_count_ is not None else recommended_processor_count()
    if workers > 1:
        int_solids = intersect_solids_parallel(_solids, b_boxes, workers)
    else:  # just use the single-core process
        int_solids = intersect_solids(_solids, b_boxes)
