# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Preview any Honeybee geometry object within the Rhino scene, including all
sub-faces and assigned shades.
-

    Args:
        _hb_objs: A Honeybee Model, Room, Face, Shade, Aperture, or Door to be
            previewed in the Rhino scene.

    Returns:
        geo: The Rhino version of the Honeybee geometry object, which will be
            visible in the Rhino scene.
"""

ghenv.Component.Name = "HB Visualize All"
ghenv.Component.NickName = 'VizAll'
ghenv.Component.Message = '1.8.1'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '1 :: Visualize'
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:  # import the core ladybug_rhino dependencies
    from ladybug_rhino.fromhoneybee import from_hb_objects
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))



if all_required_inputs(ghenv.Component):
    geo = from_hb_objects(_hb_objs)
