# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Planarize Rhino breps in a manner that allows control over the meshing process.
_
The resulting planar breps will be solid if the input brep is solid and any
planar faces of the brep will remain unchanged except for the polygonization
of curved edges.
-

    Args:
        _brep: A list of closed Rhino polysurfaces (aka. breps) to be planarized.
        _mesh_par_: Optional Rhino Meshing Parameters to describe how curved
            faces should be convereted into planar elements. These can be
            obtained from the native Grasshopper mesh Settings components.
            If None, Rhino's Default Meshing Parameters will be used, which
            tend to be very coarse and simple.
    
    Returns:
        report: Reports, errors, warnings, etc.
        pl_brep: A planar version of the input _brep.
"""

ghenv.Component.Name = "HB Planarize Brep"
ghenv.Component.NickName = 'Planarize'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.planarize import curved_solid_faces
    from ladybug_rhino.fromgeometry import from_face3ds_to_joined_brep
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # planarize each of the breps
    pl_brep = []
    for brep in _brep:
        lb_faces = curved_solid_faces(brep, _mesh_par_)
        pl_brep.extend(from_face3ds_to_joined_brep(lb_faces))
