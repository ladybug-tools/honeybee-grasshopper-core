# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

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
        _depth: A number for the extrusion depth.
        indoor_: Boolean for whether the extrusion should be generated facing the
            opposite direction of the aperture normal and added to the Aperture's
            indoor_shades instead of outdoor_shades. Note that, by default, indoor
            shades are not used in energy simulations but they are used in all
            simulations involving Radiance. Default: False.
        ep_constr_: Optional text for an energy construction to be used for all
            generated shades. This text will be used to look up a construction
            in the shade construction library. This can also be a custom
            ShadeConstruction object.
        rad_mod_: Optional text for a radiance modifier to be used for all
            generated shades. This text will be used to look up a modifier
            in the modifier library. This can also be a custom modifier object.
    
    Returns:
        report: Reports, errors, warnings, etc.
        hb_objs: The input Honeybee Face or Room or Aperture with extruded border
            shades added to it.
"""

ghenv.Component.Name = "HB Extruded Border Shades"
ghenv.Component.NickName = 'BorderShades'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.face import Aperture
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
    indoor_ = indoor_ if indoor_ is not None else False

    # get energyplus constructions if they are requested
    if ep_constr_ is not None:
        if isinstance(ep_constr_, str):
            ep_constr_ = shade_construction_by_identifier(ep_constr_)

    # get radiance modifiers if they are requested
    if rad_mod_ is not None:
        if isinstance(rad_mod_, str):
            rad_mod_ = modifier_by_identifier(rad_mod_)

    # loop through the input objects and add shades
    for obj in hb_objs:
        if isinstance(obj, Room):
            for face in obj.faces:
                for ap in face.apertures:
                    assign_shades(ap, _depth, indoor_, ep_constr_, rad_mod_)
        elif isinstance(obj, Face):
            for ap in obj.apertures:
                assign_shades(ap, _depth, indoor_, ep_constr_, rad_mod_)
        elif isinstance(obj, Aperture):
            assign_shades(obj, _depth, indoor_, ep_constr_, rad_mod_)
        else:
            raise TypeError('Input _hb_objs must be a Room, Face or Aperture. '
                            'Not {}.'.format(type(obj)))