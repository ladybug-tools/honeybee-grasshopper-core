# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create Honeybee Door
-

    Args:
        _geo: Rhino Brep or Mesh geometry.
        _name_: A name for the Door. If the name is not provided a random
            name will be assigned.
        glass_: Boolean to note whether the Door is transparent. Default: False.
        ep_constr_: Optional text for the Door's energy construction to be looked
            up in the construction library. This can also be a custom construction
            object. If no energy construction is input here, a default will be
            assigned based on the properties of the parent face that the Door
            is assigned to (ie. whether the Face is a RoofCeiling, whether it has
            a Surface boundary condition, etc.)
        rad_mod_: Optional text for the Door's radiance modifier to be looked
            up in the modifier library. This can also be a custom modifier object.
            If no radiance modifier is input here, a default will be assigned
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
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import the core honeybee dependencies
    from honeybee.door import Door
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.togeometry import to_face3d
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list, \
        wrap_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy.lib.constructions import opaque_construction_by_identifier, \
        window_construction_by_identifier
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


if all_required_inputs(ghenv.Component):
    doors = []  # list of doors that will be returned
    for j, geo in enumerate(_geo):
        if len(_name_) == 0:  # make a default Door name
            name = display_name = clean_and_id_string('Door')
        else:
            display_name = '{}_{}'.format(longest_list(_name_, j), j + 1) \
                if len(_name_) != len(_geo) else longest_list(_name_, j)
            name = clean_and_id_string(display_name)
        glass = longest_list(glass_, j) if len(glass_) != 0 else False

        lb_faces = to_face3d(geo)
        for i, lb_face in enumerate(lb_faces):
            dr_name = '{}_{}'.format(name, i) if len(lb_faces) > 1 else name
            hb_dr = Door(dr_name, lb_face, is_glass=glass)
            hb_dr.display_name = display_name

            # try to assign the energyplus construction
            if len(ep_constr_) != 0:
                ep_constr = longest_list(ep_constr_, j)
                if isinstance(ep_constr, str):
                    ep_constr = opaque_construction_by_identifier(ep_constr) if not \
                        hb_dr.is_glass else window_construction_by_identifier(ep_constr)
                hb_dr.properties.energy.construction = ep_constr

            # try to assign the radiance modifier
            if len(rad_mod_) != 0:
                rad_mod = longest_list(rad_mod_, j)
                if isinstance(rad_mod, str):
                    rad_mod = modifier_by_identifier(rad_mod)
                hb_dr.properties.radiance.modifier = rad_mod

            doors.append(hb_dr)  # collect the final Doors
            i += 1  # advance the iterator
    doors = wrap_output(doors)
