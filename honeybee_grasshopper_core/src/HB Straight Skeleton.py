# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get the straight skeleton of any horizontal planar geometry.
_
This is can also be used to generate core/perimeter sub-polygons if an offset is
input AND the straight skeleton is not self-intersecting. In the event of a
self-intersecting straight skeleton, the output line segments can still be used
to assist with the manual creation of core/perimeter offsets.
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
        polyskel: A list of line segments that represent the straight skeleton of
            the input _floor_geo. This will be output from the component no matter
            what the input _floor_geo is.
        perim_poly: A list of breps representing the perimeter polygons of the input
            _floor_geo. This will only be ouput if an offset_ is input and the
            straight skeleton is not self-intersecting.
        core_poly: A list of breps representing the core polygons of the input
            _floor_geo. This will only be ouput if an offset_ is input and the
            straight skeleton is not self-intersecting, and the offset is not
            so great as to eliminate the core.
"""

ghenv.Component.Name = 'HB Straight Skeleton'
ghenv.Component.NickName = 'Skeleton'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core ladybug_geometry dependencies
    from ladybug_geometry.geometry2d.line import LineSegment2D
    from ladybug_geometry.geometry2d.polygon import Polygon2D
    from ladybug_geometry.geometry3d.pointvector import Point3D
    from ladybug_geometry.geometry3d.face import Face3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core ladybug_geometry dependencies
    from ladybug_geometry_polyskel.polyskel import skeleton_as_edge_list
    from ladybug_geometry_polyskel.polysplit import perimeter_core_subpolygons
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.fromgeometry import from_face3d, from_linesegment2d
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def polygon_to_brep(polygon, z_height):
    """Convert a ladybug Polygon2D or list of polygon2D into Rhino breps."""
    if isinstance(polygon, list):  # face with holes
        verts = []
        for poly in polygon:
            verts.append([Point3D(pt.x, pt.y, z_height) for pt in poly])
        return from_face3d(Face3D(verts[0], holes=verts[1:]))
    else:
        verts = [Point3D(pt.x, pt.y, z_height) for pt in polygon]
        return from_face3d(Face3D(verts))


if all_required_inputs(ghenv.Component):
    # first extract the straight skeleton from the geometry
    polyskel, boundaries, hole_polygons = [], [], []
    for face in to_face3d(_floor_geo):
        # convert the input geometry into Polygon2D for straight skeleton analysis
        boundary = Polygon2D.from_array([(pt.x, pt.y) for pt in face.boundary])
        if boundary.is_clockwise:
            boundary = boundary.reverse()
        holes, z_height = None, face[0].z
        if face.has_holes:
            holes = []
            for hole in face.holes:
                h_poly = Polygon2D.from_array([(pt.x, pt.y) for pt in hole])
                if not h_poly.is_clockwise:
                    h_poly = h_poly.reverse()
                holes.append(h_poly)
        boundaries.append(boundary)
        hole_polygons.append(holes)
        # compute the skeleton and convert to line segments
        skel_lines = skeleton_as_edge_list(boundary, holes, tolerance)
        skel_lines_rh = [from_linesegment2d(LineSegment2D.from_array(line), z_height)
                         for line in skel_lines]
        polyskel.append(skel_lines_rh)

    # try to compute core/perimeter polygons if an offset_ is input
    if offset_:
        perim_poly, core_poly = [], []
        for bound, holes in zip(boundaries, hole_polygons):
            try:
                perim, core = perimeter_core_subpolygons(
                    bound, offset_, holes, tolerance)
                perim_poly.append([polygon_to_brep(p, z_height) for p in perim])
                core_poly.append([polygon_to_brep(p, z_height) for p in core])
            except RuntimeError as e:
                print(e)
                perim_poly.append(None)
                core_poly.append(None)

    # convert outputs to data trees
    polyskel = list_to_data_tree(polyskel)
    perim_poly = list_to_data_tree(perim_poly)
    core_poly = list_to_data_tree(core_poly)
