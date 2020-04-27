# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Honeybee Shade
-

    Args:
        _geo: Rhino Brep geometry.
        _name_: Text to set the name for the Shade and to be incorporated into
            unique Shade identifier. If the name is not provided, a random name
            will be assigned.
        ep_constr_: Optional text for the Shade's energy construction to be looked
            up in the construction library. This can also be a custom construction
            object. If no energy construction is input here, a default will be
            assigned.
        ep_trans_sch_: Optional text for the Shade's energy transmittance schedule
            to be looked up in the schedule library. This can also be a custom
            schedule object. If no energy schedule is input here, the default will
            be always opaque.
        rad_mod_: Optional text for the Shade's radiance modifier to be looked
            up in the modifier library. This can also be a custom modifier object.
            If no radiance modifier is input here, a default will be assigned.
    
    Returns:
        report: Reports, errors, warnings, etc.
        shades: Honeybee shades. These can be used directly in radiance and
            energy simulations.
"""

ghenv.Component.Name = "HB Shade"
ghenv.Component.NickName = 'Shade'
ghenv.Component.Message = '0.2.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

import uuid

try:  # import the core honeybee dependencies
    from honeybee.shade import Shade
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import shade_construction_by_identifier
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    if ep_constr_ is not None:
        raise ValueError('ep_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))
    elif ep_trans_sch_ is not None:
        raise ValueError('ep_trans_sch_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError as e:
    if rad_mod_ is not None:
        raise ValueError('rad_mod_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))


if all_required_inputs(ghenv.Component):
    shades = []  # list of shades that will be returned

    # set default name
    name = clean_and_id_string(_name_) if _name_ is not None else str(uuid.uuid4())

    # create the Shades
    i = 0  # iterator to ensure each shade gets a unique name
    for geo in _geo:
        for lb_face in to_face3d(geo):
            hb_shd = Shade('{}_{}'.format(name, i), lb_face)
            if _name_ is not None:
                hb_shd.display_name = '{}_{}'.format(_name_, i)

            # try to assign the energyplus construction
            if ep_constr_ is not None:
                if isinstance(ep_constr_, str):
                    ep_constr_ = shade_construction_by_identifier(ep_constr_)
                hb_shd.properties.energy.construction = ep_constr_

            # try to assign the energyplus transmittance schedule
            if ep_trans_sch_ is not None:
                if isinstance(ep_trans_sch_, str):
                    ep_trans_sch_ = schedule_by_identifier(ep_trans_sch_)
                hb_shd.properties.energy.transmittance_schedule = ep_trans_sch_

            # try to assign the radiance modifier
            if rad_mod_ is not None:
                if isinstance(rad_mod_, str):
                    rad_mod_ = modifier_by_identifier(rad_mod_)
                hb_shd.properties.radiance.modifier = rad_mod_

            shades.append(hb_shd)  # collect the final Shades
            i += 1  # advance the iterator