# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>


"""
Take a list of closed breps (polysurfaces) that you intend to turn into Rooms and
split their Faces to ensure that there are matching faces between each of the
adjacent rooms.
_
Matching faces and face areas betweem adjacent rooms are necessary to ensure
that the conductive heat flow calculation occurs correctly across the face in
an energy simulation.
-

    Args:
        _solids: A list of closed Rhino breps (polysurfaces) that you intend to turn
            into Rooms that do not have perfectly matching surfaces between
            adjacent Faces (this matching is needed to contruct a correct
            multi-room energy model).
        parallel_: Set to "True" to run the intersection calculation in parallel,
            which can greatly increase the speed of calculation but may not be
            desired when other simulations are running on your machine. If False,
            the calculation will be run on a single core. Default: False.
        _run: Set to True to run the component.
    
    Returns:
        int_solids: The same input closed breps that have had their component
            faces split by adjacent polysurfaces to have matching surfaces between
            adjacent breps.  It is recommended that you bake this output and check
            it in Rhino before turning the breps into honeybee Rooms.
"""

ghenv.Component.Name = "HB Intersect Solids"
ghenv.Component.NickName = 'IntSolid'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"


try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.intersect import intersect_solids, intersect_solids_parallel
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))



if all_required_inputs(ghenv.Component) and _run:
    # generate bounding boxes for all inputs
    b_boxes = [brep.GetBoundingBox(False) for brep in _solids]
    
    # intersect all of the solid geometries
    if parallel_:
        int_solids = intersect_solids_parallel(_solids, b_boxes)
    else:
        int_solids = intersect_solids(_solids, b_boxes)
