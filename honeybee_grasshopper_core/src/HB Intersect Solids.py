# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
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
        _run: Set to True to run the component.
    
    Returns:
        int_solids: The same input closed breps that have had their component
            faces split by adjacent polysurfaces to have matching surfaces between
            adjacent breps.  It is recommended that you bake this output and check
            it in Rhino before turning the breps into honeybee Rooms.
"""

ghenv.Component.Name = "HB Intersect Solids"
ghenv.Component.NickName = 'IntSolid'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "HoneybeeCore"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"


###############################################################################
#########################     NOTE TO DEVELOPERS    ###########################
###############################################################################
"""
The code within this component will be replaced with a much more efficient
version in its own module of ladybug_rhino shortly.
"""

from collections import deque

import Rhino.Geometry as rg
import scriptcontext
tol = scriptcontext.doc.ModelAbsoluteTolerance

try:  # import the core honeybee dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))


def intersectMasses(building, otherBldg):
    changed = False
    joinedLines = []
    done = False # keep looking until done is True

    # prevent dead loop, will break when no more intersection detected
    while(not done):
        tempBldg = building.Duplicate()
        for face1 in building.Faces:
            if face1.IsSurface:
                # if it is a untrimmed surface just find intersection lines
                intersectLines = rg.Intersect.Intersection.BrepSurface(otherBldg, face1.DuplicateSurface(), tol)[1]
            else:
                # if it is a trimmed surface
                edgesIdx = face1.AdjacentEdges()
                edges = []
                for ix in edgesIdx:
                    edges.append(building.Edges.Item[ix])
                crv = rg.Curve.JoinCurves(edges, tol)
                # potential bugs: multiple brep of one face?
                intersectLines = rg.Intersect.Intersection.BrepBrep(rg.Brep.CreatePlanarBreps(crv)[0], otherBldg, tol)[1]
            temp = rg.Curve.JoinCurves(intersectLines, tol)
            joinedLines = [crv for crv in temp if rg.Brep.CreatePlanarBreps(crv)]
            if len(joinedLines) > 0:
                newBrep = face1.Split(joinedLines, tol) # return None on Failure
                if not newBrep:
                    continue
                if newBrep.Faces.Count > building.Faces.Count:
                    changed = True
                    building = newBrep
                    break
        if tempBldg.Faces.Count == building.Faces.Count:
            done = True
    return building, changed



def main(bldgMassesBefore):
    buildingDict = {}

    for bldgCount, bldg in enumerate(bldgMassesBefore):
        buildingDict[bldgCount] = bldg
    need_change = deque(buildingDict.keys())

    i = 0 # to prevent dead loop
    while(len(need_change) > 0 and i < 10e2 * len(bldgMassesBefore)):
        bldgNum = need_change.pop()
        building = buildingDict[bldgNum]
        for num_other in buildingDict.keys():
            if num_other == bldgNum: continue
            otherBldg = buildingDict[num_other]
            building, changed = intersectMasses(building, otherBldg)
            buildingDict[bldgNum] = building
            if changed and num_other not in need_change:
                # for reinforcement of matching, not neccessary
                need_change.appendleft(num_other)
        i += 1
    return buildingDict.values()


# add an compile toggle, set _compile to True to run the function
if all_required_inputs(ghenv.Component) and _run is True:
    int_solids = main(_solids)