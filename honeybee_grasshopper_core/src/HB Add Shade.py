# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Add a Honeybee Shades to an Aperture, Door, Face or Room.
-

    Args:
        _hb_obj: A Honeybee Aperture, Door, Face or a Room to which the shades should
            be added.
        out_shades_: A list of Honeybee Shade objects to be added to the outside
            of the input _hb_objs.
        in_shades_: A list of Honeybee Shade objects to be added to the inside
            of the input _hb_objs. Note that, by default, indoor shades are not
            used in energy simulations but they are used in all simulations
            involving Radiance.
    
    Returns:
        report: Reports, errors, warnings, etc.
        hb_obj: The input Honeybee Aperture, Face or a Room with the input shades
            added to it.
"""

ghenv.Component.Name = "HB Add Shade"
ghenv.Component.NickName = 'AddShade'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "5"

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    hb_obj = _hb_obj.duplicate()  # duplicate the initial object

    if out_shades_ is not None:
        hb_obj.add_outdoor_shades((shd.duplicate() for shd in out_shades_))
    if in_shades_ is not None:
        hb_obj.add_indoor_shades((shd.duplicate() for shd in in_shades_))
