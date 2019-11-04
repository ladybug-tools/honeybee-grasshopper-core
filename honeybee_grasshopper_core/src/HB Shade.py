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
        _name_: A name for the Shade. If the name is not provided a random
            name will be assigned.
        ep_constr_: Optional text for the Shade's energy construction to be looked
            up in the construction library. This can also be a custom construction
            object. If no energy construction is input here, a default will be
            assigned.
        ep_trans_sch_: Optional text for the Shade's energy transmittance schedule
            to be looked up in the schedule library. This can also be a custom
            schedule object. If no energy schedule is input here, the default will
            be always opaque.
        rad_mat_: Optional text for the Shade's radiance material to be looked
            up in the material library. This can also be a custom material object.
            If no radiance material is input here, a default will be assigned.
    
    Returns:
        report: Reports, errors, warnings, etc.
        shades: Honeybee shades. These can be used directly in radiance and
            energy simulations.
"""

ghenv.Component.Name = "HB Shade"
ghenv.Component.NickName = 'Shade'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = "HoneybeeCore"
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

import uuid

try:
    from honeybee.shade import Shade
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the honeybee-energy dependencies
    from honeybee_energy.lib.constructions import shade_construction_by_name
    from honeybee_energy.lib.schedules import schedule_by_name
except ImportError:
    pass  # honeybee-energy is not installed and ep_constr_ will not be avaialble


if all_required_inputs(ghenv.Component):
    shades = []  # list of shades that will be returned
    
    # set default name
    name = _name_ if _name_ is not None else str(uuid.uuid4())
    
    # create the individual Doors
    for i, lb_face in enumerate(to_face3d(_geo)):
        hb_shd = Shade('{}{}'.format(name, i), lb_face)
        
        # try to assign the energyplus construction
        if ep_constr_ is not None:
            try:
                if isinstance(ep_constr_, str):
                    ep_constr_ = shade_construction_by_name(ep_constr_)
                hb_shd.properties.energy.construction = ep_constr_
            except (NameError, AttributeError):
                raise ValueError('honeybee-energy is not installed but '
                                 'ep_constr_ has been specified.')
        
        # try to assign the energyplus transmittance schedule
        if ep_trans_sch_ is not None:
            try:
                if isinstance(ep_trans_sch_, str):
                    ep_trans_sch_ = schedule_by_name(ep_trans_sch_)
                hb_shd.properties.energy.transmittance_schedule = ep_trans_sch_
            except (NameError, AttributeError):
                raise ValueError('honeybee-energy is not installed but '
                                 'ep_trans_sch_ has been specified.')
        
        # collect the final Doors
        shades.append(hb_shd)