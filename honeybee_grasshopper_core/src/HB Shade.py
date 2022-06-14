# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create Honeybee Shade
-

    Args:
        _geo: Rhino Brep or Mesh geometry.
        _name_: Text to set the name for the Shade and to be incorporated into
            unique Shade identifier. If the name is not provided, a random name
            will be assigned.
        attached_: Boolean to note whether the Shade is attached to other geometry.
            This is automatically set to True if the Shade is assigned to
            a parent Room, Face, Aperture or Door but will otherwise defalt
            to False. If the Shade is not easily assignable to a parent
            object but is attached to the building (eg. a parapet or large
            roof overhang), then this should be set to True. (Default: False).
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
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '5'

try:  # import the core honeybee dependencies
    from honeybee.shade import Shade
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
    from honeybee_energy.lib.constructions import shade_construction_by_identifier
    from honeybee_energy.lib.schedules import schedule_by_identifier
except ImportError as e:
    if len(ep_constr_) != 0:
        raise ValueError('ep_constr_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))
    elif len(ep_trans_sch_) != 0:
        raise ValueError('ep_trans_sch_ has been specified but honeybee-energy '
                         'has failed to import.\n{}'.format(e))

try:  # import the honeybee-radiance extension
    from honeybee_radiance.lib.modifiers import modifier_by_identifier
except ImportError as e:
    if len(rad_mod_) != 0:
        raise ValueError('rad_mod_ has been specified but honeybee-radiance '
                         'has failed to import.\n{}'.format(e))


if all_required_inputs(ghenv.Component):
    shades = []  # list of shades that will be returned
    for j, geo in enumerate(_geo):
        if len(_name_) == 0:  # make a default Shade name
            name = display_name = clean_and_id_string('Shade')
        else:
            display_name = '{}_{}'.format(longest_list(_name_, j), j + 1) \
                if len(_name_) != len(_geo) else longest_list(_name_, j)
            name = clean_and_id_string(display_name)
        is_detached = not longest_list(attached_, j) if len(attached_) != 0 else True

        lb_faces = to_face3d(geo)
        for i, lb_face in enumerate(lb_faces):
            shd_name = '{}_{}'.format(name, i) if len(lb_faces) > 1 else name
            hb_shd = Shade(shd_name, lb_face, is_detached)
            hb_shd.display_name = display_name

            # try to assign the energyplus construction
            if len(ep_constr_) != 0:
                ep_constr = longest_list(ep_constr_, j)
                if isinstance(ep_constr, str):
                    ep_constr = shade_construction_by_identifier(ep_constr)
                hb_shd.properties.energy.construction = ep_constr

            # try to assign the energyplus transmittance schedule
            if len(ep_trans_sch_) != 0:
                ep_trans_sch = longest_list(ep_trans_sch_, j)
                if isinstance(ep_trans_sch, str):
                    ep_trans_sch = schedule_by_identifier(ep_trans_sch)
                hb_shd.properties.energy.transmittance_schedule = ep_trans_sch

            # try to assign the radiance modifier
            if len(rad_mod_) != 0:
                rad_mod = longest_list(rad_mod_, j)
                if isinstance(rad_mod, str):
                    rad_mod = modifier_by_identifier(rad_mod)
                hb_shd.properties.radiance.modifier = rad_mod

            shades.append(hb_shd)  # collect the final Shades
            i += 1  # advance the iterator
    shades = wrap_output(shades)