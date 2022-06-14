# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
THIS COMPONENT IS INTENDED FOR ADVANCED USERS WHO UNDERSTAND THAT IDENTIFERS
SHOULD BE UNIQUE AND THAT, TO SET THEM OTHERWISE CAN HAVE UNINTENDED CONSEQUENCES.
_
Change the identifier of any Honeybee object.
_
Note that this component only changes the identifer of the input _hb_obj and
none of the identifiers of the child objects.
-

    Args:
        _hb_obj: Any honeybee-core object (eg. Room, Face, Shade, Aperture) or
            any honeybee extension object (eg. energy construction, radiance
            modifier) for which the identifier should be changed.
        _id: Text for the identifier of the object. Note that, if this identifier
            does not conform to acceptable values of the object type (eg. no
            spaces for a radiance modifier id), then an exception will be thrown.

    Returns:
        report: ...
        hb_objs: The input Honeybee object with its identifier changed.
"""

ghenv.Component.Name = 'HB Set Identifier'
ghenv.Component.NickName = 'ID'
ghenv.Component.Message = '1.5.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    hb_obj = _hb_obj.duplicate()
    hb_obj.identifier = _id
    hb_obj._display_name = None
