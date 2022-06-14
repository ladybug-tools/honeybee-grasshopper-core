# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Set the apertures of room Faces using (a) guide surface(s) or polysurface(s).
_
Faces that are touching and coplanar with the guide surface will get their
aperters changed according to the input properties.
-

    Args:
        _rooms: Honeybee Rooms which will have their apertures set based on their
            relation to the guide surface(s).
        _guide: Rhino Breps or Meshes that represent the guide surfaces.
        _ratio: A number between 0 and 0.95 for the ratio between the area of
            the apertures and the area of the parent face.
        _subdivide_: Boolean to note whether to generate a single window in the
            center of each Face (False) or to generate a series of rectangular
            windows using the other inputs below (True). The latter is often more
            realistic and is important to consider for detailed daylight and
            thermal comfort simulations but the former is likely better when the
            only concern is building energy use since energy use doesn't change
            much while the glazing ratio remains constant. (Default: True).
        _win_height_: A number for the target height of the output apertures.
            Note that, if the ratio is too large for the height, the ratio will
            take precedence and the actual aperture height will be larger
            than this value. (Default: 2 meters).
        _sill_height_: A number for the target height above the bottom edge of
            the face to start the apertures. Note that, if the ratio is too large
            for the height, the ratio will take precedence and the sill_height
            will be smaller than this value. If an array of values are input here,
            different heights will be assigned based on cardinal direction, starting
            with north and moving clockwise. Default: 0.8 meters.
        _horiz_separ_: A number for the horizontal separation between
            individual aperture centerlines.  If this number is larger than
            the parent face's length, only one aperture will be produced.
            If an array of values are input here, different separation distances
            will be assigned based on cardinal direction, starting with north
            and moving clockwise. Default: 3 meters.
        vert_separ_: An optional number to create a single vertical
            separation between top and bottom apertures. If an array of values
            are input here, different separation distances will be assigned based
            on cardinal direction, starting with north and moving clockwise.
            Default: 0.
        operable_: An optional boolean to note whether the generated Apertures
            can be opened for ventilation. If an array of booleans are input
            here, different operable properties will be assigned based on
            cardinal direction, starting with north and moving clockwise.
            Default: False.

    Returns:
        rooms: The input Rooms with their Face properties changed.
"""

ghenv.Component.Name = 'HB Apertures by Guide Surface'
ghenv.Component.NickName = 'AperturesByGuide'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
     from honeybee.boundarycondition import Outdoors
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance, angle_tolerance, conversion_to_meters
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def assign_apertures(face, sub, rat, hgt, sil, hor, vert, op):
    """Assign apertures to a Face based on a set of inputs."""
    if sub:
        face.apertures_by_ratio_rectangle(rat, hgt, sil, hor, vert, tolerance)
    else:
        face.apertures_by_ratio(rat, tolerance)

    # try to assign the operable property
    if op:
        for ap in face.apertures:
            ap.is_operable = op


if all_required_inputs(ghenv.Component):
    # process the inputs
    rooms = [room.duplicate() for room in _rooms]  # duplicate to avoid editing input
    guide_faces = [g for geo in _guide for g in to_face3d(geo)]  # convert to lb geometry
    conversion = conversion_to_meters()
    _subdivide_ = _subdivide_ if _subdivide_ is not None else True
    _win_height_ = _win_height_ if _win_height_ is not None else 2.0 / conversion
    _sill_height_ = _sill_height_ if _sill_height_ is not None else 0.8 / conversion
    _horiz_separ_ = _horiz_separ_ if _horiz_separ_ is not None else 3.0 / conversion
    vert_separ_ = vert_separ_ if vert_separ_ is not None else 0.0
    operable_ = operable_ if operable_ is not None else False

    # loop through the rooms and set the face properties
    for room in rooms:
        select_faces = room.faces_by_guide_surface(
            guide_faces, tolerance=tolerance, angle_tolerance=angle_tolerance)
        for hb_face in select_faces:
            if isinstance(hb_face.boundary_condition, Outdoors):
                assign_apertures(hb_face, _subdivide_, _ratio, _win_height_,
                                 _sill_height_, _horiz_separ_, vert_separ_, operable_)
