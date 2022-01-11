# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Add extruded border Shades to all the outdoor Apertures of an input Room, Face
or Aperture.
_
This is particularly useful for accounting for the depths of walls/roofs in Radiance
simulations or in the solar distribution calculation of EnergyPlus.
-

    Args:
        _hb_objs: A list of honeybee Rooms, Faces, or Apertures to which extruded
            border shades will be added.
        _depth: A number for the extrusion depth. If an array of values are input
            here, different depths will be assigned based on cardinal
            direction, starting with north and moving clockwise.
        indoor_: Boolean for whether the extrusion should be generated facing the
            opposite direction of the aperture normal and added to the Aperture's
            indoor_shades instead of outdoor_shades. If an array of values are
            input here, different indoor booleans will be assigned based on
            cardinal direction, starting with north and moving clockwise.
            Note that indoor shades are not used in energy simulations but
            they are used in all simulations involving Radiance. (Default: False).
        p_constr_: Optional Honeybee ShadeConstruction to be applied to the input _hb_objs.
            This can also be text for a construction to be looked up in the shade
            construction library. If an array of text or construction objects
            are input here, different constructions will be assigned based on
            cardinal direction, starting with north and moving clockwise.
        rad_mod_: Optional Honeybee Modifier to be applied to the input _hb_objs.
            This can also be text for a modifier to be looked up in the shade
            modifier library. If an array of text or modifier objects
            are input here, different modifiers will be assigned based on
            cardinal direction, starting with north and moving clockwise.

    Returns:
        report: Reports, errors, warnings, etc.
        hb_objs: The input Honeybee Face or Room or Aperture with extruded border
            shades added to it.
"""

ghenv.Component.Name = "HB Extruded Border Shades"
ghenv.Component.NickName = 'BorderShades'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.face import Aperture
    from honeybee.orientation import check_matching_inputs, angles_from_num_orient, \
        face_orient_index, inputs_by_index
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import shade_construction_by_identifier
except ImportError as e:
    if ep_constr_ is not None:
        raise ValueError('ep_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError as e:
    if rad_mod_ is not None:
        raise ValueError('rad_mod_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))


def assign_shades(aperture, depth, indoor, ep, rad):
    """Assign shades to an Aperture based on a set of inputs."""
    if isinstance(aperture.boundary_condition, Outdoors):
        new_shades = aperture.extruded_border(depth, indoor)
        
        # try to assign the energyplus construction
        if ep is not None:
            for shd in new_shades:
                shd.properties.energy.construction = ep
        # try to assign the radiance modifier
        if rad is not None:
            for shd in new_shades:
                shd.properties.radiance.modifier = rad


if all_required_inputs(ghenv.Component):
    # duplicate the initial objects
    hb_objs = [obj.duplicate() for obj in _hb_objs]

    # assign default indoor_ property
    indoor_ = indoor_ if len(indoor_) != 0 else [False]

    # process the input constructions
    if len(ep_constr_) != 0:
        for i, constr in enumerate(ep_constr_):
            if isinstance(constr, str):
                ep_constr_[i] = shade_construction_by_identifier(constr)
    else:
        ep_constr_ = [None]

    # process the input modifiers
    if len(rad_mod_) != 0:
        for i, mod in enumerate(rad_mod_):
            if isinstance(mod, str):
                rad_mod_[i] = modifier_by_identifier(mod)
    else:
        rad_mod_ = [None]

    # gather all of the inputs together
    all_inputs = [_depth, indoor_, ep_constr_, rad_mod_]

    # ensure matching list lengths across all values
    all_inputs, num_orient = check_matching_inputs(all_inputs)

    # get a list of angles used to categorize the faces
    angles = angles_from_num_orient(num_orient)

    # loop through the input objects and add shades
    for obj in hb_objs:
        if isinstance(obj, Room):
            for face in obj.faces:
                orient_i = face_orient_index(face, angles)
                if orient_i is None:
                    orient_i = 0
                depth, indr, con, mod = inputs_by_index(orient_i, all_inputs)
                for ap in face.apertures:
                    assign_shades(ap, depth, indr, con, mod)
        elif isinstance(obj, Face):
            orient_i = face_orient_index(obj, angles)
            if orient_i is None:
                orient_i = 0
            depth, indr, con, mod = inputs_by_index(orient_i, all_inputs)
            for ap in obj.apertures:
                assign_shades(ap, depth, indr, con, mod)
        elif isinstance(obj, Aperture):
            orient_i = face_orient_index(obj, angles)
            if orient_i is None:
                orient_i = 0
            depth, indr, con, mod = inputs_by_index(orient_i, all_inputs)
            assign_shades(obj, depth, indr, con, mod)
        else:
            raise TypeError('Input _hb_objs must be a Room, Face or Aperture. '
                            'Not {}.'.format(type(obj)))