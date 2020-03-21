# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Create Honeybee Door
-

    Args:
        _geo: Rhino Brep geometry.
        _name_: A name for the Door. If the name is not provided a random
            name will be assigned.
        glass_: Boolean to note whether the Door is transparent. Default: False.
        ep_constr_: Optional text for the Door's energy construction to be looked
            up in the construction library. This can also be a custom construction
            object. If no energy construction is input here, a default will be
            assigned based on the properties of the parent face that the Door
            is assigned to (ie. whether the Face is a RoofCeiling, whether it has
            a Surface boundary condition, etc.)
        rad_mat_: Optional text for the Door's radiance material to be looked
            up in the material library. This can also be a custom material object.
            If no radiance material is input here, a default will be assigned
            based on the properties of the parent face that the Door is
            assigned to (ie. whether the Face is a RoofCeiling, whether it has a
            Surface boundary condition, etc.)
    
    Returns:
        report: Reports, errors, warnings, etc.
        doors: Honeybee doors. These can be used directly in radiance
            simulations or can be added to a Honeybee face for energy simulation.
"""

ghenv.Component.Name = "HB Door"
ghenv.Component.NickName = 'Door'
ghenv.Component.Message = '0.1.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

import uuid

try:  # import the core honeybee dependencies
    from honeybee.door import Door
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import opaque_construction_by_name, \
        window_construction_by_name
except ImportError as e:
    if ep_constr_ is not None:
        raise ValueError('ep_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    import honeybee_radiance
except ImportError as e:
    if rad_mat_ is not None:
        raise ValueError('rad_mat_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))


if all_required_inputs(ghenv.Component):
    doors = []  # list of doors that will be returned
    
    # set default name
    name = _name_ if _name_ is not None else str(uuid.uuid4())
    
    # create the Doors
    i = 0  # iterator to ensure each door gets a unique name
    for geo in _geo:
        for lb_face in to_face3d(geo):
            hb_dr = Door('{}_{}'.format(name, i), lb_face, is_glass=glass_)
            
            # try to assign the energyplus construction
            if ep_constr_ is not None:
                if isinstance(ep_constr_, str):
                    ep_constr_ = opaque_construction_by_name(ep_constr_) if not \
                        hb_dr.is_glass else window_construction_by_name(ep_constr_)
                hb_dr.properties.energy.construction = ep_constr_
            
            doors.append(hb_dr)  # collect the final Doors
            i += 1  # advance the iterator