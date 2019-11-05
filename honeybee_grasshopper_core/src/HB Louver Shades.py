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
        _hb_obj: A list of honeybee Rooms, Faces, or Apertures to which louver
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
        ep_trans_sch_: Optional text for the Shade's energy transmittance schedule
            to be looked up in the schedule library. This can also be a custom
            schedule object. If no energy schedule is input here, the default
            will be always opaque. If an array of text or schedule objects
            are input here, different schedules will be assigned based on
            cardinal direction, starting with north and moving clockwise.
        rad_mat_: Optional text for a radiance material to be used for all
            generated shades. This text will be used to look up a material
            in the material library. This can also be a custom material object.
            If an array of text or material objects are input here, different
            materials will be assigned based on cardinal direction, starting
            with north and moving clockwise.
        _run: Set to True to run the component.
    
    Returns:
        report: Reports, errors, warnings, etc.
        hb_obj: The input Honeybee Face or Room or Aperture with louvered shades
            added to it.
"""

ghenv.Component.Name = "HB Louver Shades"
ghenv.Component.NickName = 'LouverShades'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "HoneybeeCore"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.face import Aperture
    from honeybee.facetype import Wall
    from ladybug_geometry.geometry2d.pointvector import Vector2D
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.schedules import schedule_by_name
except ImportError as e:
    if len(ep_trans_sch_) != 0:
        raise ValueError('ep_trans_sch_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    import honeybee_radiance
except ImportError as e:
    if len(rad_mat_) != 0:
        raise ValueError('rad_mat_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))


def can_host_louvers(face):
    """Test if a face is intended to host louvers (according to this component)."""
    return isinstance(face.boundary_condition, Outdoors) and \
        isinstance(face.type, Wall)


def assign_louvers(ap, depth, count, dist, off, angle, vec, flip, indr, sch, rad):
    """Assign louvers to an Aperture based on a set of inputs."""
    if count is not None:
        louvers = ap.louvers_by_count(count, depth, off, angle, vec, flip, indr,
                                      tolerance)
    else:
        louvers = ap.louvers_by_distance_between(dist, depth, off, angle, vec,
                                       flip, indr, tolerance)
    
    # try to assign the energyplus transmittance schedule
    if sch is not None:
        for shd in louvers:
            shd.properties.energy.transmittance_schedule = sch


def orient_index(orient, angles):
    """Get the index to be used for a given orientation in a list of angles."""
    for i, ang in enumerate(angles):
        if orient < ang:
            return i
    return 0


def inputs_by_index(count, all_inputs):
    """Get all of the inputs of a certain index from a list of all_inputs."""
    return (inp[count] for inp in all_inputs)


if all_required_inputs(ghenv.Component) and _run:
    # duplicate the initial objects
    hb_obj = [obj.duplicate() for obj in _hb_obj]
    
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
    
    # get energyplus constructions if they are requested
    if len(ep_trans_sch_) != 0:
        for i, sch in enumerate(ep_trans_sch_):
            if isinstance(sch, str):
                ep_trans_sch_[i] = schedule_by_name(sch)
    else:
        ep_trans_sch_ = [None]
    
    # get the radiance material (set to None for now).
    rad_mat_ = [None]
    
    # gather all of the inputs together
    all_inputs = [_depth, _shade_count_, _dist_between_, _facade_offset_, _angle_,
                  vertical_, flip_start_, indoor_, ep_trans_sch_, rad_mat_]
    
    # ensure matching list lengths across all values
    num_orient = len(_depth)
    for i, param_list in enumerate(all_inputs):
        if len(param_list) == 1:
            all_inputs[i] = param_list * num_orient
        else:
            assert len(param_list) == num_orient, \
                'The number of items in one of the inputs lists does not match the ' \
                'number of items in the _ratio list.\nPlease ensure that either ' \
                'the lists match or you put in a single value for all orientations.'
    
    # get a list of angles used to categorize the faces
    step = 360.0 / num_orient
    start = step / 2.0
    angles = []
    while start < 360:
        angles.append(start)
        start += step
    
    # loop through the input objects and add apertures
    for obj in hb_obj:
        if isinstance(obj, Room):
            for face in obj.faces:
                if can_host_louvers(face):
                    orient_i = orient_index(face.horizontal_orientation(), angles)
                    depth, count, dist, off, angle, vec, flip, indr, sch, rad = \
                        inputs_by_index(orient_i, all_inputs)
                    for ap in face.apertures:
                        assign_louvers(ap, depth, count, dist, off, angle, vec,
                                       flip, indr, sch, rad)
        elif isinstance(obj, Face):
            if can_host_apeture(obj):
                orient_i = orient_index(face.horizontal_orientation(), angles)
                depth, count, dist, off, angle, vec, flip, indr, sch, rad = \
                    inputs_by_index(orient_i, all_inputs)
                for ap in face.apertures:
                    assign_louvers(ap, depth, count, dist, off, angle, vec,
                                   flip, indr, sch, rad)
        elif isinstance(obj, Aperture):
            orient_i = orient_index(obj.horizontal_orientation(), angles)
            depth, count, dist, off, angle, vec, flip, indr, sch, rad = \
                inputs_by_index(orient_i, all_inputs)
            assign_louvers(obj, depth, count, dist, off, angle, vec, flip, indr,
                           sch, rad)
        else:
            raise TypeError(
                'Input _hb_obj must be a Room, Face, or Aperture. Not {}.'.format(type(obj)))