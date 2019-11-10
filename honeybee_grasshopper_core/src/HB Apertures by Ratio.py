# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Add apertures to a Honeybee Face or Room given a ratio of aperture area to face area.
_
Note that this component will only add Apertures to Faces that are Walls and have
an Outdoors boundary condition.
-

    Args:
        _hb_obj: A list of honeybee Rooms or Faces to which Apertures will be
            added based on the inputs.
        _ratio: A number between 0 and 0.95 for the ratio between the area of
            the apertures and the area of the parent face. If an array of values
            are input here, different ratios will be assigned based on
            cardinal direction, starting with north and moving clockwise.
        _subdivide_: Boolean to note whether to generate a single window in the
            center of each Face (False) or to generate a series of rectangular
            windows using the other inputs below (True). The latter is often more
            realistic and is important to consider for detailed daylight and
            thermal comfort simulations but the former is likely better when the
            only concern is building energy use since energy use doesn't change
            much while the glazing ratio remains constant. Default: True.
        _glz_height_: A number for the target height of the output apertures.
            Note that, if the ratio is too large for the height, the ratio will
            take precedence and the actual aperture height will be larger
            than this value. If an array of values are input here, different
            heights will be assigned based on cardinal direction, starting with
            north and moving clockwise. Default: 2 meters.
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
        ep_constr_: Optional text for an energy construction to be used for all
            generated apertures. This text will be used to look up a construction
            in the window construction library. This can also be a custom
            WindowConstruction object. If an array of text or construction objects
            are input here, different constructions will be assigned based on
            cardinal direction, starting with north and moving clockwise.
        rad_mat_: Optional text for a radiance material to be used for all
            generated apertures. This text will be used to look up a material
            in the material library. This can also be a custom material object.
            If an array of text or material objects are input here, different
            materials will be assigned based on cardinal direction, starting
            with north and moving clockwise.
        _run: Set to True to run the component.
    
    Returns:
        report: Reports, errors, warnings, etc.
        hb_obj: The input Honeybee Face or Room with Apertures generated from
            the input parameters.
"""

ghenv.Component.Name = "HB Apertures by Ratio"
ghenv.Component.NickName = 'AperturesByRatio'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "HoneybeeCore"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors
    from honeybee.facetype import Wall
    from honeybee.room import Room
    from honeybee.face import Face
    from ladybug_rhino.config import tolerance, conversion_to_meters
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import window_construction_by_name
    from honeybee_energy.construction.window import WindowConstruction
except ImportError as e:
    if len(ep_constr_) != 0:
        raise ValueError('ep_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    import honeybee_radiance
except ImportError as e:
    if len(rad_mat_) != 0:
        raise ValueError('rad_mat_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))


def can_host_apeture(face):
    """Test if a face is intended to host apertures (according to this component)."""
    return isinstance(face.boundary_condition, Outdoors) and \
        isinstance(face.type, Wall)


def assign_apertures(face, sub, rat, hgt, sil, hor, vert, op, ep, rad):
    """Assign apertures to a Face based on a set of inputs."""
    if sub:
        face.apertures_by_ratio_rectangle(rat, hgt, sil, hor, vert, tolerance)
    else:
        face.apertures_by_ratio(rat, tolerance)
    
    # try to assign the operable property
    if op:
        for ap in face.apertures:
            ap.is_operable = op
    
    # try to assign the energyplus construction
    if ep is not None:
        for ap in face.apertures:
            ap.properties.energy.construction = ep


def orient_index(face_orient, angles):
    """Get the index to be used for a given face orientation in a list of angles."""
    for i, ang in enumerate(angles):
        if face_orient < ang:
            return i
    return 0


def inputs_by_index(count, all_inputs):
    """Get all of the inputs of a certain index from a list of all_inputs."""
    return (inp[count] for inp in all_inputs)


if all_required_inputs(ghenv.Component) and _run:
    # duplicate the initial objects
    hb_obj = [obj.duplicate() for obj in _hb_obj]
    
    # set defaults for any blank inputs
    conversion = conversion_to_meters()
    _subdivide_ = _subdivide_ if len(_subdivide_) != 0 else [True]
    _glz_height_ = _glz_height_ if len(_glz_height_) != 0 else [2.0 / conversion]
    _sill_height_ = _sill_height_ if len(_sill_height_) != 0 else [0.8 / conversion]
    _horiz_separ_ = _horiz_separ_ if len(_horiz_separ_) != 0 else [3.0 / conversion]
    vert_separ_ = vert_separ_ if len(vert_separ_) != 0 else [0.0]
    operable_ = operable_ if len(operable_) != 0 else [False]
    
    # get energyplus constructions if they are requested
    if len(ep_constr_) != 0:
        for i, constr in enumerate(ep_constr_):
            if isinstance(constr, str):
                ep_constr_[i] = window_construction_by_name(constr)
    else:
        ep_constr_ = [None]
    
    # get the radiance material (set to None for now).
    rad_mat_ = [None]
    
    # gather all of the inputs together
    all_inputs = [_subdivide_, _ratio, _glz_height_, _sill_height_, _horiz_separ_,
                  vert_separ_, operable_, ep_constr_, rad_mat_]
    
    # ensure matching list lengths across all values
    num_orient = len(_ratio)
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
                if can_host_apeture(face):
                    orient_i = orient_index(face.horizontal_orientation(), angles)
                    sub, rat, hgt, sil, hor, vert, op, ep, rad = \
                        inputs_by_index(orient_i, all_inputs)
                    assign_apertures(face, sub, rat, hgt, sil, hor, vert, op, ep, rad)
        elif isinstance(obj, Face):
            if can_host_apeture(obj):
                orient_i = orient_index(face.horizontal_orientation(), angles)
                sub, rat, hgt, sil, hor, vert, op, ep, rad = \
                    inputs_by_index(orient_i, all_inputs)
                assign_apertures(obj, sub, rat, hgt, sil, hor, vert, op, ep, rad)
        else:
            raise TypeError(
                'Input _hb_obj must be a Room or Face. Not {}.'.format(type(obj)))