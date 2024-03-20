# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Add apertures to a Honeybee Face or Room given a width and a height of windows
that repeat across the walls at a specific horizontal separation between window
centerlines.
_
Note that this component will only add Apertures to Faces that are Walls, have
an Outdoors boundary condition, and have at least a portion of the Face that
is clearly rectangular.
-

    Args:
        _hb_objs: A list of honeybee Rooms or Faces to which Apertures will be
            added based on the inputs. This can also be an entire honeybee
            Model for which all Rooms will have Apertures assigned.
        _win_height_: A number for the target height of the output apertures. Note
            that, if the window height is larger than the height of the wall, the
            generated windows will have a height equal to the wall height in
            order to avoid having windows extend outside the wall face. If an
            array of values are input here, different heights will be assigned
            based on cardinal direction, starting with north and moving
            clockwise. (Default: 2 meters).
        _win_width_: A number for the target width the output apertures. Note that,
            if the window width is larger than the width of the wall, the
            generated windows will have a width equal to the wall width in
            order to avoid having windows extend outside the wall face. If an
            array of values are input here, different widths will be assigned
            based on cardinal direction, starting with north and moving
            clockwise. (Default: 1.5 meters).
        _sill_height_: A number for the target height above the bottom edge of the face to
            start the apertures. Note that, if the window height is too large
            to acoomodate the sill height input here, the window height will take
            precedence and the sill height will be smaller than this value. If
            an array of values are input here, different heights will be assigned
            based on cardinal direction, starting with north and moving
            clockwise. (Default: 0.8 meters).
        _horiz_separ_: A number for the horizontal separation between individual aperture
            centerlines.  If this number is larger than the parent face's length,
            only one aperture will be produced. If an array of values are input
            here, different separation distances will be assigned based on cardinal
            direction, starting with north and moving clockwise. (Default: 3 meters).
        operable_: An optional boolean to note whether the generated Apertures can be
            opened for ventilation. If an array of booleans are input here, different
            operable properties will be assigned based on cardinal direction,
            starting with north and moving clockwise. (Default: False).

    Returns:
        report: Reports, errors, warnings, etc.
        hb_objs: The input Honeybee Face, Room or Model with Apertures generated from
            the input parameters.
"""

ghenv.Component.Name = 'HB Apertures by Width Height'
ghenv.Component.NickName = 'AperturesByWH'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors
    from honeybee.facetype import Wall
    from honeybee.face import Face
    from honeybee.room import Room
    from honeybee.model import Model
    from honeybee.orientation import check_matching_inputs, angles_from_num_orient, \
        face_orient_index, inputs_by_index
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance, conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def can_host_apeture(face):
    """Test if a face is intended to host apertures (according to this component)."""
    return isinstance(face.boundary_condition, Outdoors) and \
        isinstance(face.type, Wall)


def assign_apertures(face, hgt, wth, sil, hor, op):
    """Assign apertures to a Face based on a set of inputs."""
    face.apertures_by_width_height_rectangle(hgt, wth, sil, hor, tolerance)

    # try to assign the operable property
    if op:
        for ap in face.apertures:
            ap.is_operable = op


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_objs = [obj.duplicate() for obj in _hb_objs]

    # set defaults for any blank inputs
    conversion = conversion_to_meters()
    _win_height_ = _win_height_ if len(_win_height_) != 0 else [2.0 / conversion]
    _win_width_ = _win_width_ if len(_win_width_) != 0 else [1.5 / conversion]
    _sill_height_ = _sill_height_ if len(_sill_height_) != 0 else [0.8 / conversion]
    _horiz_separ_ = _horiz_separ_ if len(_horiz_separ_) != 0 else [3.0 / conversion]
    operable_ = operable_ if len(operable_) != 0 else [False]

    # gather all of the inputs together
    all_inputs = [_win_height_, _win_width_, _sill_height_, _horiz_separ_, operable_]

    # ensure matching list lengths across all values
    all_inputs, num_orient = check_matching_inputs(all_inputs)

    # get a list of angles used to categorize the faces
    angles = angles_from_num_orient(num_orient)

    # loop through the input objects and add apertures
    for obj in hb_objs:
        if isinstance(obj, Model):
            for room in obj.rooms:
                for face in room.faces:
                    if can_host_apeture(face):
                        orient_i = face_orient_index(face, angles)
                        hgt, wth, sil, hor, op = inputs_by_index(orient_i, all_inputs)
                        assign_apertures(face, hgt, wth, sil, hor, op)
        elif isinstance(obj, Room):
            for face in obj.faces:
                if can_host_apeture(face):
                    orient_i = face_orient_index(face, angles)
                    hgt, wth, sil, hor, op = inputs_by_index(orient_i, all_inputs)
                    assign_apertures(face, hgt, wth, sil, hor, op)
        elif isinstance(obj, Face):
            if can_host_apeture(obj):
                orient_i = face_orient_index(obj, angles)
                hgt, wth, sil, hor, op = inputs_by_index(orient_i, all_inputs)
                assign_apertures(obj, hgt, wth, sil, hor, op)
        else:
            raise TypeError(
                'Input _hb_objs must be a Mode, Room or Face. Not {}.'.format(type(obj)))