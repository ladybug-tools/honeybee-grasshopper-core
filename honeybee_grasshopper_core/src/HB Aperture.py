# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create Honeybee Aperture
-

    Args:
        _geo: Rhino Brep or Mesh geometry.
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
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"

try:  # import the core honeybee dependencies
    from honeybee.aperture import Aperture
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
    from honeybee_energy.lib.constructions import window_construction_by_identifier
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
    apertures = []  # list of apertures that will be returned
    for j, geo in enumerate(_geo):
        if len(_name_) == 0:  # make a default Aperture name
            name = display_name = clean_and_id_string('Aperture')
        else:
            display_name = '{}_{}'.format(longest_list(_name_, j), j + 1) \
                if len(_name_) != len(_geo) else longest_list(_name_, j)
            name = clean_and_id_string(display_name)
        operable = longest_list(operable_, j) if len(operable_) != 0 else False

        lb_faces = to_face3d(geo)
        for i, lb_face in enumerate(lb_faces):
            ap_name = '{}_{}'.format(name, i) if len(lb_faces) > 1 else name
            hb_ap = Aperture(ap_name, lb_face, is_operable=operable)
            hb_ap.display_name = display_name

            # try to assign the energyplus construction
            if len(ep_constr_) != 0:
                ep_constr = longest_list(ep_constr_, j)
                if isinstance(ep_constr, str):
                    ep_constr = window_construction_by_identifier(ep_constr)
                hb_ap.properties.energy.construction = ep_constr

            # try to assign the radiance modifier
            if len(rad_mod_) != 0:
                rad_mod = longest_list(rad_mod_, j)
                if isinstance(rad_mod, str):
                    rad_mod = modifier_by_identifier(rad_mod)
                hb_ap.properties.radiance.modifier = rad_mod

            apertures.append(hb_ap)  # collect the final Apertures
            i += 1  # advance the iterator
    apertures = wrap_output(apertures)