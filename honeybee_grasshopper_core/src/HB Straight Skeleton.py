# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get the straight skeleton and core/perimeter sub-faces for any planar geometry.
_
This component uses a modified version of the the polyskel package
(https://github.com/Botffy/polyskel) by Armin Scipiades (aka. @Bottfy),
which is, itself, a Python implementation of the straight skeleton
algorithm as described by Felkel and Obdrzalek in their 1998 conference paper
Straight skeleton implementation
(https://github.com/Botffy/polyskel/blob/master/doc/StraightSkeletonImplementation.pdf).
-

    Args:
        _floor_geo: Horizontal Rhino surfaces for which the straight skeleton
            will be computed.
        offset_: An optional positive number that will be used to offset the
            perimeter of the geometry to output core/perimeter polygons.
            If a value is plugged in here and the straight skeleton is not
            self-intersecting, perim_poly and core_poly will be ouput.

    Returns:
        report: Reports, errors, warnings, etc.
        skeleton: A list of line segments that represent the straight skeleton of
            the input _floor_geo. This will be output from the component no matter
            what the input _floor_geo is.
        perim_poly: A list of breps representing the perimeter polygons of the input
            _floor_geo. This will only be ouput if an offset_ is input.
        core_poly: A list of breps representing the core polygons of the input
            _floor_geo. This will only be ouput if an offset_ is input and the offset
            is not so great as to eliminate the core.
"""

ghenv.Component.Name = 'HB Straight Skeleton'
ghenv.Component.NickName = 'Skeleton'
ghenv.Component.Message = '1.8.3'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core ladybug_geometry dependencies
    from ladybug_geometry.geometry3d import LineSegment3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core ladybug_geometry dependencies
    from ladybug_geometry_polyskel.polyskel import skeleton_as_edge_list
    from ladybug_geometry_polyskel.polysplit import perimeter_core_subfaces_and_skeleton
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.fromgeometry import from_face3d, from_linesegment3d
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # extract the straight skeleton and sub-faces from the geometry
    skeleton, perim_poly, core_poly = [], [], []
    for face in to_face3d(_floor_geo):
        face = face.remove_colinear_vertices(tolerance)
        if offset_ is not None and offset_ > 0:
            skel, perim, core = perimeter_core_subfaces_and_skeleton(
                face, offset_, tolerance)
            skeleton.extend([from_linesegment3d(lin) for lin in skel])
            perim_poly.extend([from_face3d(p) for p in perim])
            core_poly.extend([from_face3d(c) for c in core])
        else:
            skel_2d = skeleton_as_edge_list(
                face.boundary_polygon2d, face.hole_polygon2d,
                tolerance, intersect=True)
            skel_3d = []
            for seg in skel_2d:
                verts_3d = tuple(face.plane.xy_to_xyz(pt) for pt in seg.vertices)
                skel_3d.append(LineSegment3D.from_end_points(*verts_3d))
            skeleton.extend([from_linesegment3d(lin) for lin in skel_3d])
