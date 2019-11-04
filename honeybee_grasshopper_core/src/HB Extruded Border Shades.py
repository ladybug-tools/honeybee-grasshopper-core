# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
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
        _hb_obj: A list of honeybee Rooms, Faces, or Apertures to which extruded
            border shades will be added.
        _depth: A number for the extrusion depth.
        indoor_: Boolean for whether the extrusion should be generated facing the
            opposite direction of the aperture normal and added to the Aperture's
            indoor_shades instead of outdoor_shades. Default: False.
        ep_constr_: Optional text for an energy construction to be used for all
            generated shades. This text will be used to look up a construction
            in the shade construction library. This can also be a custom
            ShadeConstruction object.
        rad_mat_: Optional text for a radiance material to be used for all
            generated shades. This text will be used to look up a material
            in the material library. This can also be a custom material object.
        _run: Set to True to run the component.
    
    Returns:
        report: Reports, errors, warnings, etc.
        hb_obj: The input Honeybee Face or Room or Aperture with extruded border
            shades added to it.
"""

ghenv.Component.Name = "HB Extruded Border Shades"
ghenv.Component.NickName = 'BorderShades'
ghenv.Component.Message = '0.1.0\nOCT_28_2019'
ghenv.Component.Category = "HoneybeeCore"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the core honeybee dependencies
    from honeybee.boundarycondition import Outdoors
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.face import Aperture
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.lib.constructions import shade_construction_by_name
    from honeybee_energy.construction.shade import ShadeConstruction
except ImportError:
    pass  # honeybee-energy is not installed and ep_constr_ will not be avaialble


def assign_shades(aperture, depth, indoor, ep, rad):
    """Assign shades to an Aperture based on a set of inputs."""
    if isinstance(aperture.boundary_condition, Outdoors):
        new_shades = aperture.extruded_border(depth, indoor)
        
        # try to assign the energyplus construction
        if ep is not None:
            for shd in new_shades:
                shd.properties.energy.construction = ep


if all_required_inputs(ghenv.Component) and _run is True:
    # duplicate the initial objects
    hb_obj = [obj.duplicate() for obj in _hb_obj]
    
    # assign default indoor_ property
    indoor_ = indoor_ if indoor_ is not None else False
    
    # get energyplus constructions if they are requested
    if ep_constr_ is not None:
        try:
            if isinstance(ep_constr_, str):
                ep_constr_ = shade_construction_by_name(ep_constr_)
            else:
                assert isinstance(ep_constr_, ShadeConstruction), \
                    'Expected WindowConstruction for ep_constr_. ' \
                    'Got {}.'.format(type(ep_constr_))
        except (NameError, AttributeError):
            raise ValueError('honeybee-energy is not installed but '
                             'ep_constr_ has been specified.')
    
    # loop through the input objects and add shades
    for obj in hb_obj:
        if isinstance(obj, Room):
            for face in obj.faces:
                for ap in face.apertures:
                    assign_shades(ap, _depth, indoor_, ep_constr_, rad_mat_)
        elif isinstance(obj, Face):
            for ap in obj.apertures:
                assign_shades(ap, _depth, indoor_, ep_constr_, rad_mat_)
        elif isinstance(obj, Aperture):
            assign_shades(obj, _depth, indoor_, ep_constr_, rad_mat_)
        else:
            raise TypeError('Input _hb_obj must be a Room, Face or Aperture. '
                            'Not {}.'.format(type(obj)))