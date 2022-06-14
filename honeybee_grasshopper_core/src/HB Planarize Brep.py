# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

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
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "2"

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.planarize import curved_solid_faces
    from ladybug_rhino.fromgeometry import from_face3ds_to_joined_brep
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # planarize each of the breps
    pl_brep, smaller_than_tol = [], set()
    for i, brep in enumerate(_brep):
        lb_faces = curved_solid_faces(brep, _mesh_par_, ignore_sliver=False)
        all_lb_faces = []
        for face in lb_faces:
            if face is not None:
                all_lb_faces.append(face)
            else:
                smaller_than_tol.add(i)
        pl_brep.extend(from_face3ds_to_joined_brep(all_lb_faces))

    # if one of the breps has slivers smaller than the tolerance, give a warning
    if smaller_than_tol:
        base_rec = 'Consider lowering the Rhino model tolernace and restarting ' \
            'Rhino to get a better planar representation'
        for brep_i in smaller_than_tol:
            msg = 'Brep at index {} could not be perfectly planarized at ' \
                'the current Rhino model tolernace and may have gaps or ' \
                'holes.\n{}.'.format(brep_i, base_rec)
            print(msg)
            give_warning(ghenv.Component, msg)
