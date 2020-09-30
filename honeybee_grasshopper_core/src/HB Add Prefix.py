# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Change the display name and identifier of this object and all child objects by
inserting a prefix.
_
This is particularly useful in workflows where you duplicate and edit
a starting object and then want to combine it with the original object
into one Model (like making a model of repeated rooms) since all objects
within a Model must have unique identifiers.
-

    Args:
        _hb_objs: A Honeybee Room, Face, Shade, Aperture, or Door to which a
            prefix should be added to its name.
        _prefix: Text that will be inserted at the start of this object's
            (and child objects') identifier and display_name. This will also be
            added to any Surface boundary conditions of Faces, Apertures, or
            Doors. It is recommended that this prefix be short to avoid maxing
            out the 100 allowable characters for honeybee identifiers. This can
            also be a list of prefixes that correspond to the input _hb_objs
    
    Returns:
        report: ...
        hb_objs: The input Honeybee objects with a prefix added to their display
            names and identifiers.
"""

ghenv.Component.Name = "HB Add Prefix"
ghenv.Component.NickName = 'Prefix'
ghenv.Component.Message = '1.0.0'
ghenv.Component.Category = 'Honeybee'
ghenv.Component.SubCategory = '0 :: Create'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.grasshopper import all_required_inputs, longest_list
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    hb_objs = []
    for i, obj in enumerate(_hb_objs):
        obj_dup = obj.duplicate()
        prefix = longest_list(_prefix, i)
        obj_dup.add_prefix(prefix)
        hb_objs.append(obj_dup)