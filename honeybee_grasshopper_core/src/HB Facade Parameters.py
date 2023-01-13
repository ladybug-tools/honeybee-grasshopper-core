# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Generate lists of facadce properties ordanized by the four primary cardinal
directions.
_
Such properties can be glazing ratios, glazing heigths, sill heights, horizontal/
vertical glazing splits for the "HB Apertures by Ratio" component. Or they could
be shade depths, angles, etc. for the "HB Louver Shades" component.
-

    Args:
        _north_: Glazing parameter (boolean, float) for the north.
        _east_: Glazing parameter (boolean, float) for the east.
        _south_: Glazing parameter (boolean, float) for the south.
        _west_: Glazing parameter (boolean, float) for the west.
    
    Returns:
        fac_par: A list of properties for different cardinal directions to be
            plugged into the "HB Apertures by Ratio" component or the "HB Louver
            Shades" component.
"""
ghenv.Component.Name = "HB Facade Parameters"
ghenv.Component.NickName = 'FacParam'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = "4"


def check_param(parameter):
    if isinstance(parameter, bool):
        return parameter
    try:
        return float(parameter)
    except (TypeError, AttributeError, ValueError):
        return parameter


fac_par = [check_param(par) for par in (_north_, _east_, _south_, _west_)]
