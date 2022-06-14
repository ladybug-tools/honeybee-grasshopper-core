# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

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
            If there is an input below for _dist_between_, an attempt will
            still be made to meet the _shade_count_ but, if there are more
            shades than can fit on the input hb_obj, the number of shades
            will be truncated. If an array of values are input here, different
            shade counts will be assigned based on cardinal direction, starting
            with north and moving clockwise. (Default: 1).
        _dist_between_: A number for the approximate distance between each louver.
            If an array of values are input here, different distances between
            louvers will be assigned based on cardinal direction, starting
            with north and moving clockwise.
        _facade_offset_: A number for the distance from the louver edge to the
            facade. If an array of values are input here, different offsets will
            be assigned based on cardinal direction, starting with north and
            moving clockwise. (Default: 0).
        _angle_: A number for the for an angle to rotate the louvers in degrees.
            If an array of values are input here, different angles will be
            assigned based on cardinal direction, starting with north and moving
            clockwise. (Default: 0).
        vertical_: Optional boolean to note whether the lovers are vertical. If False,
            the louvers will be horizontal. If an array of values are input
            here, different vertical booleans will be assigned based on cardinal
            direction, starting with north and moving clockwise. (Default: False).
        flip_start_: Optional boolean to note whether the side the louvers start
            from should be flipped. If False, louvers will be generated starting
            on top or the right side. If True, louvers will start from the
            bottom or left. If an array of values are input here, different
            flip start booleans will be assigned based on cardinal direction,
            starting with north and moving clockwise. Default: False.
        indoor_: Optional boolean for whether louvers should be generated facing the
            opposite direction of the aperture normal and added to the Aperture's
            indoor_shades instead of outdoor_shades. If an array of values are
            input here, different indoor booleans will be assigned based on
            cardinal direction, starting with north and moving clockwise.
            Note that, by default, indoor shades are not used in energy simulations
            but they are used in all simulations involving Radiance. (Default: False).
        ep_constr_: Optional Honeybee ShadeConstruction to be applied to the input _hb_objs.
            This can also be text for a construction to be looked up in the shade
            construction library. If an array of text or construction objects
            are input here, different constructions will be assigned based on
            cardinal direction, starting with north and moving clockwise.
        ep_trans_sch_: Optional schedule for the transmittance to be applied to the
            input _hb_objs in energy simulation. If no energy schedule is
            input here, the default will be always opaque.
        rad_mod_: Optional Honeybee Modifier to be applied to the input _hb_objs.
            This can also be text for a modifier to be looked up in the shade
            modifier library. If an array of text or modifier objects
            are input here, different modifiers will be assigned based on
            cardinal direction, starting with north and moving clockwise.

    Returns:
        report: Reports, errors, warnings, etc.
        hb_objs: The input Honeybee Face or Room or Aperture with louvered shades
            added to it.
"""

ghenv.Component.Name = "HB Louver Shades"
ghenv.Component.NickName = 'LouverShades'
ghenv.Component.Message = '1.5.0'
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

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import shade_construction_by_identifier
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    if len(ep_constr_) != 0:
        raise ValueError('ep_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError as e:
    if len(rad_mod_) != 0:
        raise ValueError('rad_mod_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def can_host_louvers(face):
    """Test if a face is intended to host louvers (according to this component)."""
    return isinstance(face.boundary_condition, Outdoors) and \
        isinstance(face.type, Wall)


def assign_louvers(ap, depth, count, dist, off, angle, vec, flip, indr, ep, ep_tr, rad):
    """Assign louvers to an Aperture based on a set of inputs."""
    if depth == 0 or count == 0:
        return None
    if dist is None:
        louvers = ap.louvers_by_count(
            count, depth, off, angle, vec, flip, indr, tolerance)
    else:
        louvers = ap.louvers_by_distance_between(
            dist, depth, off, angle, vec, flip, indr, tolerance, max_count=count)

    # try to assign the energyplus construction and transmittance schedule
    if ep is not None:
        for shd in louvers:
            shd.properties.energy.construction = ep
    if ep_tr is not None:
        for shd in louvers:
            shd.properties.energy.transmittance_schedule = ep_tr
    # try to assign the radiance modifier
    if rad is not None:
        for shd in louvers:
            shd.properties.radiance.modifier = rad


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_objs = [obj.duplicate() for obj in _hb_objs]

    # set defaults for any blank inputs
    _facade_offset_ = _facade_offset_ if len(_facade_offset_) != 0 else [0.0]
    _angle_ = _angle_ if len(_angle_) != 0 else [0.0]
    flip_start_ = flip_start_ if len(flip_start_) != 0 else [False]
    indoor_ = indoor_ if len(indoor_) != 0 else [False]

    # process the defaults for _shade_count_ vs _dist_between
    if len(_shade_count_) != 0 and len(_dist_between_) != 0:
        pass
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

    # process the input constructions and shade transmittances
    if len(ep_constr_) != 0:
        for i, constr in enumerate(ep_constr_):
            if isinstance(constr, str):
                ep_constr_[i] = shade_construction_by_identifier(constr)
    else:
        ep_constr_ = [None]
    if len(ep_trans_sch_) != 0:
        for i, sch in enumerate(ep_trans_sch_):
            if isinstance(sch, str):
                ep_trans_sch_[i] = schedule_by_identifier(sch)
    else:
        ep_trans_sch_ = [None]

    # process the input modifiers
    if len(rad_mod_) != 0:
        for i, mod in enumerate(rad_mod_):
            if isinstance(mod, str):
                rad_mod_[i] = modifier_by_identifier(mod)
    else:
        rad_mod_ = [None]

    # gather all of the inputs together
    all_inputs = [_depth, _shade_count_, _dist_between_, _facade_offset_, _angle_,
                  vertical_, flip_start_, indoor_, ep_constr_, ep_trans_sch_, rad_mod_]

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
                    depth, count, dist, off, angle, vec, flip, indr, con, sh_t, mod = \
                        inputs_by_index(orient_i, all_inputs)
                    for ap in face.apertures:
                        assign_louvers(ap, depth, count, dist, off, angle, vec,
                                       flip, indr, con, sh_t, mod)
        elif isinstance(obj, Face):
            if can_host_louvers(obj):
                orient_i = face_orient_index(obj, angles)
                depth, count, dist, off, angle, vec, flip, indr, con, sh_t, mod = \
                    inputs_by_index(orient_i, all_inputs)
                for ap in obj.apertures:
                    assign_louvers(ap, depth, count, dist, off, angle, vec,
                                   flip, indr, con, sh_t, mod)
        elif isinstance(obj, Aperture):
            orient_i = face_orient_index(obj, angles)
            depth, count, dist, off, angle, vec, flip, indr, con, sh_t, mod = \
                inputs_by_index(orient_i, all_inputs)
            assign_louvers(obj, depth, count, dist, off, angle, vec, flip,
                           indr, con, sh_t, mod)
        else:
            raise TypeError(
                'Input _hb_objs must be a Room, Face, or Aperture. Not {}.'.format(type(obj)))