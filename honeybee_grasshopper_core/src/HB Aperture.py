# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Honeybee Aperture
-

    Args:
        _geo: Rhino Brep geometry.
        _name_: Text to set the name for the Aperture and to be incorporated into
            unique Aperture identifier. If the name is not provided, a random name
            will be assigned.
        operable_: Boolean to note whether the Aperture can be opened for ventilation.
            Default: False.
        ep_constr_: Optional text for the Aperture's energy construction to be looked
            up in the construction library. This can also be a custom WindowConstruction
            object. If no energy construction is input here, a default will be
            assigned based on the properties of the parent face that the Aperture
            is assigned to (ie. whether the Face is a RoofCeiling, whether it has
            a Surface boundary condition, etc.)
        rad_mod_: Optional text for the Aperture's radiance modifier to be looked
            up in the modifier library. This can also be a custom modifier object.
            If no radiance modifier is input here, a default will be assigned
            based on the properties of the parent face that the Aperture is
            assigned to (ie. whether the Face is a RoofCeiling, whether it has a
            Surface boundary condition, etc.)
    
    Returns:
        report: Reports, errors, warnings, etc.
        apertures: Honeybee apertures. These can be used directly in radiance
            simulations or can be added to a Honeybee face for energy simulation.
"""

ghenv.Component.Name = "HB Aperture"
ghenv.Component.NickName = 'Aperture'
ghenv.Component.Message = '0.2.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

import uuid

try:  # import the core honeybee dependencies
    from honeybee.aperture import Aperture
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import window_construction_by_identifier
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


if all_required_inputs(ghenv.Component):
    apertures = []  # list of apertures that will be returned

    # set default name
    name = clean_and_id_string(_name_) if _name_ is not None else str(uuid.uuid4())

    # create the Apertures
    i = 0  # iterator to ensure each aperture gets a unique name
    for geo in _geo:
        for lb_face in to_face3d(geo):
            hb_ap = Aperture('{}_{}'.format(name, i), lb_face, is_operable=operable_)
            if _name_ is not None:
                hb_ap.display_name = '{}_{}'.format(_name_, i)

            # try to assign the energyplus construction
            if ep_constr_ is not None:
                if isinstance(ep_constr_, str):
                    ep_constr_ = window_construction_by_identifier(ep_constr_)
                hb_ap.properties.energy.construction = ep_constr_

            # try to assign the radiance modifier
            if rad_mod_ is not None:
                if isinstance(rad_mod_, str):
                    rad_mod_ = modifier_by_identifier(rad_mod_)
                hb_ap.properties.radiance.modifier = rad_mod_

            apertures.append(hb_ap)  # collect the final Apertures
            i += 1  # advance the iterator