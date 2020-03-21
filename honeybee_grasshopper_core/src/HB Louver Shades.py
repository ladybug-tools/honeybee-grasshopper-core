# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Add louverd Shades, overhangs or fins to all the outdoor Apertures of an input
Room, Face or Aperture.
_
Note that, if a Face or Room is input, Shades will only be added to those Faces
that are Walls (not Floors or Roofs).
-

    Args:
        _hb_objs: A list of honeybee Rooms, Faces, or Apertures to which louver
            shades will be added.
        _depth: A number for the depth to extrude the louvers. If an array of values
            are input here, different depths will be assigned based on
            cardinal direction, starting with north and moving clockwise.
        _shade_count_: A positive integer for the number of louvers to generate.
            Note that this input should be None if there is an input for
            _dist_between_. If an array of values are input here, different
            shade counts will be assigned based on cardinal direction, starting
            with north and moving clockwise. Default: 1.
        _dist_between_: A number for the approximate distance between each louver.
            Note that this input should be None if there is an input for
            _shade_count_. If an array of values are input here, different
            distances between louvers will be assigned based on cardinal
            direction, starting with north and moving clockwise.
        _facade_offset_: A number for the distance from the louver edge to the
            facade. If an array of values are input here, different offsets will
            be assigned based on cardinal direction, starting with north and
            moving clockwise. Default: 0.
        _angle_: A number for the for an angle to rotate the louvers in degrees.
            If an array of values are input here, different angles will be
            assigned based on cardinal direction, starting with north and moving
            clockwise. Default: 0.
        vertical_: Optional boolean to note whether the lovers are vertical.
            If False, the louvers will be horizontal. If an array of values are
            input here, different vertical booleans will be assigned based on
            cardinal direction, starting with north and moving clockwise.
            Default: False.
        flip_start_: Optional boolean to note whether the side the louvers start
            from should be flipped. If False, louvers will be generated starting
            on top or the right side. If True, louvers will start contours from
            the bottom or left. If an array of values are input here, different
            flip start booleans will be assigned based on cardinal direction,
            starting with north and moving clockwise. Default: False.
        indoor_: Optional boolean for whether louvers should be generated facing the
            opposite direction of the aperture normal and added to the Aperture's
            indoor_shades instead of outdoor_shades. If an array of values are
            input here, different indoor booleans will be assigned based on
            cardinal direction, starting with north and moving clockwise.
            Note that, by default, indoor shades are not used in energy simulations
            but they are used in all simulations involving Radiance. Default: False.
        _run: Set to True to run the component.
    
    Returns:
        report: Reports, errors, warnings, etc.
        hb_objs: The input Honeybee Face or Room or Aperture with louvered shades
            added to it.
"""

ghenv.Component.Name = "HB Louver Shades"
ghenv.Component.NickName = 'LouverShades'
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the ladybug_geometry dependencies
    from ladybug_geometry.geometry2d.pointvector import Vector2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.face import Aperture
    from honeybee.facetype import Wall
    from honeybee.orientation import check_matching_inputs, angles_from_num_orient, \
        face_orient_index, inputs_by_index
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def can_host_louvers(face):
    """Test if a face is intended to host louvers (according to this component)."""
    return isinstance(face.boundary_condition, Outdoors) and \
        isinstance(face.type, Wall)


def assign_louvers(ap, depth, count, dist, off, angle, vec, flip, indr):
    """Assign louvers to an Aperture based on a set of inputs."""
    if count is not None:
        louvers = ap.louvers_by_count(count, depth, off, angle, vec, flip, indr,
                                      tolerance)
    else:
        louvers = ap.louvers_by_distance_between(dist, depth, off, angle, vec,
                                       flip, indr, tolerance)


if all_required_inputs(ghenv.Component) and _run:
    # duplicate the initial objects
    hb_objs = [obj.duplicate() for obj in _hb_objs]
    
    # set defaults for any blank inputs
    _facade_offset_ = _facade_offset_ if len(_facade_offset_) != 0 else [0.0]
    _angle_ = _angle_ if len(_angle_) != 0 else [0.0]
    flip_start_ = flip_start_ if len(flip_start_) != 0 else [False]
    indoor_ = indoor_ if len(indoor_) != 0 else [False]
    
    # process the defaults for _shade_count_ vs _dist_between
    if len(_shade_count_) != 0 and len(_dist_between_) != 0:
        raise ValueError('Inputs for _shade_count_ and _dist_between_ are both set.'
                         '\nThis component accepts either method but not both.')
    elif len(_shade_count_) == 0 and len(_dist_between_) == 0:
        _shade_count_ = [1]
        _dist_between_ = [None]
    elif len(_shade_count_) != 0:
        _dist_between_ = [None]
    else:
        _shade_count_ = [None]
    
    # process the vertical_ input into a direction vector
    if len(vertical_) != 0:
        vertical_ = [Vector2D(1, 0) if vert else Vector2D(0, 1)
                     for vert in vertical_]
    else:
        vertical_ = [Vector2D(0, 1)]
    
    # gather all of the inputs together
    all_inputs = [_depth, _shade_count_, _dist_between_, _facade_offset_, _angle_,
                  vertical_, flip_start_, indoor_]
    
    # ensure matching list lengths across all values
    all_inputs, num_orient = check_matching_inputs(all_inputs)
    
    # get a list of angles used to categorize the faces
    angles = angles_from_num_orient(num_orient)
    
    # loop through the input objects and add apertures
    for obj in hb_objs:
        if isinstance(obj, Room):
            for face in obj.faces:
                if can_host_louvers(face):
                    orient_i = face_orient_index(face, angles)
                    depth, count, dist, off, angle, vec, flip, indr = \
                        inputs_by_index(orient_i, all_inputs)
                    for ap in face.apertures:
                        assign_louvers(ap, depth, count, dist, off, angle, vec,
                                       flip, indr)
        elif isinstance(obj, Face):
            if can_host_apeture(obj):
                orient_i = face_orient_index(obj, angles)
                depth, count, dist, off, angle, vec, flip, indr = \
                    inputs_by_index(orient_i, all_inputs)
                for ap in face.apertures:
                    assign_louvers(ap, depth, count, dist, off, angle, vec,
                                   flip, indr)
        elif isinstance(obj, Aperture):
            orient_i = face_orient_index(obj, angles)
            depth, count, dist, off, angle, vec, flip, indr = \
                inputs_by_index(orient_i, all_inputs)
            assign_louvers(obj, depth, count, dist, off, angle, vec, flip, indr)
        else:
            raise TypeError(
                'Input _hb_objs must be a Room, Face, or Aperture. Not {}.'.format(type(obj)))